import logging
from datetime import datetime
from typing import Dict, List, Set, Tuple
from sqlalchemy import and_
from sqlalchemy.orm import Session

from models import Entry, DiaryItem, User

logger = logging.getLogger(__name__)

class InsertError(Exception):
    """データ挿入エラー"""
    pass

class DataInserter:
    """テストデータ挿入クラス"""

    # 日付フォーマット
    DATE_FORMAT = '%Y/%m/%d'
    DATETIME_FORMAT = '%Y/%m/%d %H:%M:%S'

    # バッチサイズ
    BATCH_SIZE = 100

    # エラーメッセージ
    ERROR_MESSAGES = {
        'user_not_found': 'ユーザーが存在しません: {}',
        'invalid_date': '無効な日付フォーマット: {}',
        'insert_failed': 'データ挿入に失敗しました: {}',
        'delete_failed': 'データ削除に失敗しました: {}',
        'no_entries': '挿入するエントリーが存在しません',
        'invalid_entry': '無効なエントリーデータ: {}'
    }

    def __init__(self, session: Session):
        self.session = session

    def get_existing_users(self, user_ids: Set[str]) -> Dict[str, User]:
        """既存ユーザーの取得"""
        users = {
            user.userid: user for user in 
            self.session.query(User).filter(User.userid.in_(user_ids)).all()
        }

        missing_users = user_ids - set(users.keys())
        if missing_users:
            raise InsertError(
                self.ERROR_MESSAGES['user_not_found'].format(
                    ', '.join(missing_users)
                )
            )

        return users

    def get_existing_entries(self, user_ids: List[int]) -> Set[Tuple[int, str]]:
        """既存エントリーの取得"""
        return {
            (entry.user_id, entry.created_at.strftime(self.DATE_FORMAT))
            for entry in self.session.query(Entry).filter(
                Entry.user_id.in_(user_ids)
            ).all()
        }

    def create_entry(self, entry_data: Dict, user: User) -> Entry:
        """エントリーの作成"""
        try:
            date = datetime.strptime(entry_data['date'], self.DATE_FORMAT)
        except ValueError:
            raise InsertError(
                self.ERROR_MESSAGES['invalid_date'].format(entry_data['date'])
            )

        entry = Entry(
            user_id=user.id,
            title=entry_data['title'],
            content=entry_data['content'],
            notes=entry_data['notes'],
            created_at=date
        )

        # 活動項目の追加
        if 'items' in entry_data:
            for item_data in entry_data['items']:
                item = DiaryItem(
                    item_name=item_data['item_name'],
                    item_content=item_data['item_content'],
                    created_at=date
                )
                entry.items.append(item)

        return entry

    def insert_entries(self, entries: List[Dict], dry_run: bool = False) -> int:
        """エントリーの一括挿入"""
        if not entries:
            raise InsertError(self.ERROR_MESSAGES['no_entries'])

        inserted_count = 0
        
        try:
            # ユーザーIDの存在確認
            user_ids = {entry['user_id'] for entry in entries}
            existing_users = self.get_existing_users(user_ids)

            # 重複チェック用のセット
            existing_entries = self.get_existing_entries(
                [user.id for user in existing_users.values()]
            )

            # バッチ処理でエントリーを挿入
            batch = []
            for entry_data in entries:
                user = existing_users[entry_data['user_id']]

                # 重複チェック
                if (user.id, entry_data['date']) in existing_entries:
                    logger.info(
                        f'重複エントリーをスキップ: {entry_data["user_id"]}, '
                        f'{entry_data["date"]}'
                    )
                    continue

                entry = self.create_entry(entry_data, user)
                batch.append(entry)
                inserted_count += 1

                # バッチサイズに達したらコミット
                if len(batch) >= self.BATCH_SIZE:
                    if not dry_run:
                        self.session.bulk_save_objects(batch)
                        self.session.commit()
                        logger.info(f'{len(batch)}件のエントリーを挿入')
                    batch = []

            # 残りのバッチを処理
            if batch and not dry_run:
                self.session.bulk_save_objects(batch)
                self.session.commit()
                logger.info(f'{len(batch)}件のエントリーを挿入')

            if dry_run:
                self.session.rollback()
                logger.info(f'{inserted_count}件のエントリーが挿入可能（ドライラン）')
            else:
                logger.info(f'合計{inserted_count}件のエントリーを挿入')

        except Exception as e:
            self.session.rollback()
            raise InsertError(self.ERROR_MESSAGES['insert_failed'].format(str(e)))

        return inserted_count

    def check_conflicts(self, entries: List[Dict]) -> List[Dict]:
        """既存データとの競合をチェック"""
        conflicts = []
        
        try:
            # ユーザーIDの取得
            user_ids = {entry['user_id'] for entry in entries}
            users = self.get_existing_users(user_ids)

            # 既存エントリーの取得
            for entry_data in entries:
                user = users[entry_data['user_id']]
                try:
                    date = datetime.strptime(entry_data['date'], self.DATE_FORMAT)
                except ValueError:
                    raise InsertError(
                        self.ERROR_MESSAGES['invalid_date'].format(
                            entry_data['date']
                        )
                    )

                # 同じ日のエントリーを検索
                existing = self.session.query(Entry).filter(
                    and_(
                        Entry.user_id == user.id,
                        Entry.created_at == date
                    )
                ).first()

                if existing:
                    conflicts.append({
                        'user_id': entry_data['user_id'],
                        'date': entry_data['date'],
                        'existing_entry': {
                            'id': existing.id,
                            'title': existing.title,
                            'created_at': existing.created_at.strftime(
                                self.DATETIME_FORMAT
                            )
                        }
                    })
                    logger.info(
                        f'競合を検出: {entry_data["user_id"]}, {entry_data["date"]}'
                    )

            return conflicts

        except Exception as e:
            raise InsertError(str(e))

    def delete_entries(self, start_date: datetime = None, end_date: datetime = None,
                      user_id: str = None) -> int:
        """エントリーの削除"""
        try:
            query = self.session.query(Entry)

            if start_date:
                query = query.filter(Entry.created_at >= start_date)
            if end_date:
                query = query.filter(Entry.created_at <= end_date)
            if user_id:
                query = query.join(User).filter(User.userid == user_id)

            count = query.count()
            query.delete(synchronize_session=False)
            self.session.commit()

            logger.info(f'{count}件のエントリーを削除')
            return count

        except Exception as e:
            self.session.rollback()
            raise InsertError(self.ERROR_MESSAGES['delete_failed'].format(str(e)))
