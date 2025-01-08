import json
import logging
import os
import shutil
from datetime import datetime
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class BackupError(Exception):
    """バックアップ操作エラー"""
    pass

class DatabaseBackup:
    """データベースバックアップ管理クラス"""

    # ファイル名のフォーマット
    BACKUP_NAME_FORMAT = 'diary_backup_{timestamp}'
    PRE_RESTORE_NAME_FORMAT = 'pre_restore_backup_{timestamp}'
    TIMESTAMP_FORMAT = '%Y%m%d_%H%M%S'
    DATETIME_FORMAT = '%Y/%m/%d %H:%M:%S'

    # ファイルサイズ制限（100MB）
    MAX_BACKUP_SIZE = 100 * 1024 * 1024

    # 必須メタデータフィールド
    REQUIRED_METADATA = ['operation', 'timestamp']

    def __init__(self, backup_dir: str):
        self.backup_dir = backup_dir
        os.makedirs(backup_dir, exist_ok=True)
        logger.info(f'バックアップディレクトリを初期化: {backup_dir}')

    def validate_metadata(self, metadata: Dict) -> None:
        """メタデータの検証"""
        for field in self.REQUIRED_METADATA:
            if field not in metadata:
                raise BackupError(f'必須メタデータが存在しません: {field}')

        if 'operation' not in metadata:
            raise BackupError('操作タイプが指定されていません')

        try:
            datetime.strptime(metadata['timestamp'], self.DATETIME_FORMAT)
        except ValueError:
            raise BackupError(
                f'無効な日時フォーマット: {metadata["timestamp"]} '
                f'(expected format: {self.DATETIME_FORMAT})'
            )

    def check_file_size(self, file_path: str) -> None:
        """ファイルサイズの検証"""
        size = os.path.getsize(file_path)
        if size > self.MAX_BACKUP_SIZE:
            raise BackupError(
                f'ファイルサイズが制限を超えています: {size} bytes '
                f'(max: {self.MAX_BACKUP_SIZE} bytes)'
            )

    def create_backup(self, db_path: str, metadata: Optional[Dict] = None) -> str:
        """データベースのバックアップを作成"""
        if not os.path.exists(db_path):
            raise BackupError(f'データベースファイルが見つかりません: {db_path}')

        # ファイルサイズの検証
        self.check_file_size(db_path)

        # バックアップファイル名の生成
        timestamp = datetime.now().strftime(self.TIMESTAMP_FORMAT)
        backup_name = self.BACKUP_NAME_FORMAT.format(timestamp=timestamp)
        
        try:
            # データベースファイルのコピー
            db_backup_path = os.path.join(self.backup_dir, f'{backup_name}.db')
            shutil.copy2(db_path, db_backup_path)
            logger.info(f'データベースファイルをバックアップ: {db_backup_path}')

            # メタデータの保存
            if metadata:
                # メタデータの検証
                metadata.update({
                    'timestamp': datetime.now().strftime(self.DATETIME_FORMAT),
                    'original_path': db_path
                })
                self.validate_metadata(metadata)

                metadata_path = os.path.join(self.backup_dir, f'{backup_name}.json')
                with open(metadata_path, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, ensure_ascii=False, indent=2)
                logger.info(f'メタデータを保存: {metadata_path}')

            return db_backup_path

        except Exception as e:
            # エラー時はバックアップファイルを削除
            if os.path.exists(db_backup_path):
                os.remove(db_backup_path)
            if metadata and os.path.exists(metadata_path):
                os.remove(metadata_path)
            raise BackupError(f'バックアップの作成に失敗しました: {str(e)}')

    def restore_backup(self, backup_path: str, target_path: str) -> None:
        """バックアップからデータベースを復元"""
        if not os.path.exists(backup_path):
            raise BackupError(f'バックアップファイルが見つかりません: {backup_path}')

        # ファイルサイズの検証
        self.check_file_size(backup_path)

        try:
            # 既存のデータベースファイルのバックアップを作成
            if os.path.exists(target_path):
                timestamp = datetime.now().strftime(self.TIMESTAMP_FORMAT)
                pre_restore_backup = os.path.join(
                    self.backup_dir,
                    f'{self.PRE_RESTORE_NAME_FORMAT.format(timestamp=timestamp)}.db'
                )
                shutil.copy2(target_path, pre_restore_backup)
                logger.info(f'既存データベースをバックアップ: {pre_restore_backup}')

            # バックアップからの復元
            shutil.copy2(backup_path, target_path)
            logger.info(f'バックアップを復元: {backup_path} -> {target_path}')

        except Exception as e:
            raise BackupError(f'バックアップの復元に失敗しました: {str(e)}')

    def list_backups(self) -> Dict[str, Dict]:
        """利用可能なバックアップの一覧を取得"""
        backups = {}
        
        try:
            # .dbファイルとそれに対応する.jsonファイルを探す
            for filename in os.listdir(self.backup_dir):
                if filename.endswith('.db'):
                    backup_name = filename[:-3]  # .dbを除いた部分
                    backup_path = os.path.join(self.backup_dir, filename)
                    metadata_path = os.path.join(self.backup_dir, f'{backup_name}.json')
                    
                    backup_info = {
                        'path': backup_path,
                        'created_at': datetime.fromtimestamp(
                            os.path.getctime(backup_path)
                        ).strftime(self.DATETIME_FORMAT),
                        'size': os.path.getsize(backup_path)
                    }

                    # メタデータファイルが存在する場合は読み込む
                    if os.path.exists(metadata_path):
                        with open(metadata_path, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                            self.validate_metadata(metadata)
                            backup_info['metadata'] = metadata

                    backups[backup_name] = backup_info

            return backups

        except Exception as e:
            raise BackupError(f'バックアップ一覧の取得に失敗しました: {str(e)}')

    def delete_backup(self, backup_name: str) -> None:
        """指定されたバックアップを削除"""
        db_path = os.path.join(self.backup_dir, f'{backup_name}.db')
        json_path = os.path.join(self.backup_dir, f'{backup_name}.json')

        if not os.path.exists(db_path):
            raise BackupError(f'バックアップファイルが見つかりません: {backup_name}')

        try:
            # データベースファイルの削除
            os.remove(db_path)
            logger.info(f'バックアップファイルを削除: {db_path}')

            # メタデータファイルが存在する場合は削除
            if os.path.exists(json_path):
                os.remove(json_path)
                logger.info(f'メタデータファイルを削除: {json_path}')

        except Exception as e:
            raise BackupError(f'バックアップの削除に失敗しました: {str(e)}')

    def cleanup_old_backups(self, keep_days: int = 30) -> None:
        """古いバックアップを削除"""
        if keep_days < 0:
            raise BackupError('保持日数は0以上である必要があります')

        try:
            current_time = datetime.now()
            backups = self.list_backups()
            deleted_count = 0

            for backup_name, info in backups.items():
                created_at = datetime.strptime(info['created_at'], self.DATETIME_FORMAT)
                age_days = (current_time - created_at).days

                if age_days > keep_days:
                    self.delete_backup(backup_name)
                    deleted_count += 1

            logger.info(f'古いバックアップを削除: {deleted_count}件')

        except Exception as e:
            raise BackupError(f'古いバックアップの削除に失敗しました: {str(e)}')
