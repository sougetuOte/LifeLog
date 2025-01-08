#!/usr/bin/env python
import json
import logging
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional

import yaml
from sqlalchemy.orm import Session

# プロジェクトのルートディレクトリをPYTHONPATHに追加
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models import Entry, DiaryItem, User
from database import get_db

from .generator import TestDataGenerator
from .validator import DataValidator
from .backup import DatabaseBackup
from .inserter import DataInserter

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y/%m/%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class TestDataManager:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_dir = os.path.join(self.base_dir, 'config')
        self.data_dir = os.path.join(self.base_dir, 'data')
        self.backup_dir = os.path.join(self.base_dir, 'backups')
        
        self.load_config()
        self.db = get_db()
        self.validator = DataValidator()

    def load_config(self):
        """設定ファイルの読み込み"""
        config_path = os.path.join(self.config_dir, 'config.yaml')
        if not os.path.exists(config_path):
            self.create_default_config()
        
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)

    def create_default_config(self):
        """デフォルト設定ファイルの作成"""
        default_config = {
            'templates': {
                'titles': [
                    '日記 - {date}',
                    '{weather}の一日'
                ],
                'contents': [
                    '今日は{activity}をした。',
                    '{feeling}一日だった。'
                ],
                'notes': {
                    'weather': ['晴れ', '曇り', '雨'],
                    'feeling': ['楽しい', '充実した', '疲れた']
                },
                'items': ['運動', '読書', '勉強']
            },
            'generation': {
                'default_rate': 100,
                'default_items_per_entry': 3,
                'output_dir': self.data_dir
            },
            'database': {
                'backup_before_clear': True,
                'backup_dir': self.backup_dir
            }
        }
        
        os.makedirs(self.config_dir, exist_ok=True)
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.backup_dir, exist_ok=True)
        
        config_path = os.path.join(self.config_dir, 'config.yaml')
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(default_config, f, allow_unicode=True, sort_keys=False)

    def generate_data(self, start_date: str, end_date: str, rate: int = 100, items_per_entry: int = 3, output: Optional[str] = None) -> str:
        """テストデータの生成"""
        # パラメータの検証
        start = self.validator.validate_date(start_date)
        end = self.validator.validate_date(end_date)
        if start > end:
            raise ValueError('開始日は終了日以前である必要があります')
        
        self.validator.validate_rate(rate)
        self.validator.validate_items_per_entry(items_per_entry)

        # 出力ファイル名の生成
        if output is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output = f'test_data_{timestamp}.json'
        
        if not os.path.isabs(output):
            output = os.path.join(self.data_dir, output)

        # データ生成
        generator = TestDataGenerator(self.config['templates'])
        entries = generator.generate_entries(
            start_date=start,
            end_date=end,
            rate=rate,
            items_per_entry=items_per_entry
        )
        test_data = {
            'metadata': {
                'generated_at': datetime.now().strftime('%Y/%m/%d %H:%M:%S'),
                'parameters': {
                    'start_date': start_date,
                    'end_date': end_date,
                    'rate': rate,
                    'items_per_entry': items_per_entry
                }
            },
            'entries': entries
        }

        # 出力ディレクトリの作成
        os.makedirs(os.path.dirname(output), exist_ok=True)

        # JSONファイルへの書き出し
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False, indent=2)

        logger.info(f'テストデータを生成しました: {output}')
        return output

    def clear_data(self, start_date: Optional[str] = None, end_date: Optional[str] = None, 
                  user: Optional[str] = None, all_data: bool = False, confirm: bool = True) -> None:
        """DBデータの削除"""
        if not any([start_date, end_date, user, all_data]):
            raise ValueError('削除条件を指定してください')

        # バックアップの作成
        if self.config['database']['backup_before_clear']:
            self.backup_database()

        # 削除対象の特定
        with Session(self.db) as session:
            query = session.query(Entry)
            
            if not all_data:
                if start_date:
                    start = self.validator.validate_date(start_date)
                    query = query.filter(Entry.created_at >= start)
                if end_date:
                    end = self.validator.validate_date(end_date)
                    query = query.filter(Entry.created_at <= end)
                if user:
                    query = query.join(User).filter(User.userid == user)

            # 削除対象の件数確認
            count = query.count()
            
            # 確認プロンプト
            if confirm:
                msg = f'以下のデータを削除します:\n'
                if all_data:
                    msg += '- 全データ\n'
                else:
                    if start_date:
                        msg += f'- 開始日: {start_date}\n'
                    if end_date:
                        msg += f'- 終了日: {end_date}\n'
                    if user:
                        msg += f'- ユーザー: {user}\n'
                msg += f'- 対象件数: {count}件\n'
                msg += '\n続行しますか？ (y/N): '
                
                if input(msg).lower() != 'y':
                    logger.info('削除をキャンセルしました')
                    return

            # データの削除
            query.delete(synchronize_session=False)
            session.commit()
            
            logger.info(f'{count}件のデータを削除しました')

    def backup_database(self) -> None:
        """データベースのバックアップを作成"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = os.path.join(self.backup_dir, f'diary_backup_{timestamp}.db')
        
        # データベースのバックアップを作成
        backup = DatabaseBackup(self.backup_dir)
        metadata = {
            'operation': 'backup',
            'timestamp': datetime.now().strftime('%Y/%m/%d %H:%M:%S'),
            'description': 'データ削除前の自動バックアップ'
        }
        backup.create_backup('instance/diary.db', metadata)
        logger.info(f'データベースのバックアップを作成しました: {backup_path}')

    def insert_data(self, file: str, dry_run: bool = False, skip_validation: bool = False) -> None:
        """テストデータの挿入"""
        # JSONファイルの読み込み
        try:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            raise ValueError(f'JSONファイルの読み込みに失敗しました: {e}')

        # バリデーション
        if not skip_validation:
            self.validator.validate_test_data(data)

        # データ挿入の実行
        with Session(self.db) as session:
            inserter = DataInserter(session)
            
            # 競合チェック
            conflicts = inserter.check_conflicts(data['entries'])
            if conflicts and not skip_validation:
                conflict_details = '\n'.join(
                    f"- ユーザー: {c['user_id']}, 日付: {c['date']}" 
                    for c in conflicts
                )
                raise ValueError(
                    f'以下のエントリーが既に存在します:\n{conflict_details}'
                )

            # 挿入実行
            count = inserter.insert_entries(data['entries'], dry_run=dry_run)
            
            if dry_run:
                logger.info(f'{count}件のエントリーが挿入可能です（ドライラン）')
            else:
                logger.info(f'{count}件のエントリーを挿入しました')

    def interactive(self) -> None:
        """対話モードの実行"""
        while True:
            print('\nテストデータ管理ツール\n')
            print('1. データ生成')
            print('2. データ削除')
            print('3. データ挿入')
            print('4. 終了\n')

            try:
                choice = input('選択してください (1-4): ')
                if choice == '1':
                    self.interactive_generate()
                elif choice == '2':
                    self.interactive_clear()
                elif choice == '3':
                    self.interactive_insert()
                elif choice == '4':
                    print('\n終了します。')
                    break
                else:
                    print('\n無効な選択です。1から4の数字を入力してください。')
            except Exception as e:
                logger.error(f'エラーが発生しました: {e}')

    def interactive_generate(self) -> None:
        """対話モードでのデータ生成"""
        print('\n=== データ生成 ===')
        try:
            start_date = input('開始日 (YYYY/MM/DD): ')
            end_date = input('終了日 (YYYY/MM/DD): ')
            rate = input('生成率 (1-100%) [100]: ') or '100'
            items = input('活動項目数 (0-10) [3]: ') or '3'
            output = input('出力ファイル名 [自動生成]: ') or None

            self.generate_data(
                start_date=start_date,
                end_date=end_date,
                rate=int(rate),
                items_per_entry=int(items),
                output=output
            )
        except Exception as e:
            logger.error(f'データ生成に失敗しました: {e}')

    def interactive_clear(self) -> None:
        """対話モードでのデータ削除"""
        print('\n=== データ削除 ===')
        print('削除範囲を選択してください:')
        print('1. 全データ')
        print('2. 日付範囲指定')
        print('3. ユーザー指定')
        print('4. 戻る\n')

        try:
            choice = input('選択してください (1-4): ')
            if choice == '1':
                self.clear_data(all_data=True)
            elif choice == '2':
                start_date = input('開始日 (YYYY/MM/DD): ')
                end_date = input('終了日 (YYYY/MM/DD): ')
                self.clear_data(start_date=start_date, end_date=end_date)
            elif choice == '3':
                user = input('ユーザーID: ')
                self.clear_data(user=user)
            elif choice == '4':
                return
            else:
                print('\n無効な選択です。')
        except Exception as e:
            logger.error(f'データ削除に失敗しました: {e}')

    def interactive_insert(self) -> None:
        """対話モードでのデータ挿入"""
        print('\n=== データ挿入 ===')
        try:
            file = input('JSONファイル: ')
            dry_run = input('ドライラン実行 (y/N): ').lower() == 'y'
            skip_validation = input('バリデーションをスキップ (y/N): ').lower() == 'y'

            self.insert_data(
                file=file,
                dry_run=dry_run,
                skip_validation=skip_validation
            )
        except Exception as e:
            logger.error(f'データ挿入に失敗しました: {e}')
