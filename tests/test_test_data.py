import os
import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from manage_test_data.validator import DataValidator, ValidationError
from manage_test_data.generator import TestDataGenerator, GeneratorError
from manage_test_data.backup import DatabaseBackup, BackupError
from manage_test_data.inserter import DataInserter, InsertError

# テストデータ
VALID_TEMPLATES = {
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
}

@pytest.fixture
def validator():
    return DataValidator()

@pytest.fixture
def generator():
    return TestDataGenerator(VALID_TEMPLATES)

@pytest.fixture
def backup(tmp_path):
    return DatabaseBackup(str(tmp_path))

@pytest.fixture
def inserter(session):
    return DataInserter(session)

class TestValidator:
    def test_validate_date(self, validator):
        # 正常系
        date = validator.validate_date('2024/01/01')
        assert isinstance(date, datetime)
        assert date.year == 2024
        assert date.month == 1
        assert date.day == 1

        # 異常系
        with pytest.raises(ValidationError):
            validator.validate_date('2024-01-01')  # 不正なフォーマット
        with pytest.raises(ValidationError):
            validator.validate_date('2024/13/01')  # 不正な月
        with pytest.raises(ValidationError):
            validator.validate_date('2024/01/32')  # 不正な日

    def test_validate_rate(self, validator):
        # 正常系
        validator.validate_rate(1)
        validator.validate_rate(50)
        validator.validate_rate(100)

        # 異常系
        with pytest.raises(ValidationError):
            validator.validate_rate(0)  # 範囲外（下限）
        with pytest.raises(ValidationError):
            validator.validate_rate(101)  # 範囲外（上限）
        with pytest.raises(ValidationError):
            validator.validate_rate('50')  # 不正な型

    def test_validate_items_per_entry(self, validator):
        # 正常系
        validator.validate_items_per_entry(0)
        validator.validate_items_per_entry(3)
        validator.validate_items_per_entry(10)

        # 異常系
        with pytest.raises(ValidationError):
            validator.validate_items_per_entry(-1)  # 負の値
        with pytest.raises(ValidationError):
            validator.validate_items_per_entry('3')  # 不正な型

class TestGenerator:
    def test_validate_templates(self, generator):
        # 正常系
        generator.validate_templates(VALID_TEMPLATES)

        # 異常系
        invalid_templates = VALID_TEMPLATES.copy()
        invalid_templates['titles'] = []  # 空のリスト
        with pytest.raises(GeneratorError):
            generator.validate_templates(invalid_templates)

    def test_generate_entries(self, generator):
        # 正常系
        start_date = datetime.now()
        end_date = start_date + timedelta(days=5)
        entries = generator.generate_entries(
            start_date=start_date,
            end_date=end_date,
            rate=100,
            items_per_entry=3
        )

        assert len(entries) > 0
        for entry in entries:
            assert 'user_id' in entry
            assert 'date' in entry
            assert 'title' in entry
            assert 'content' in entry
            assert 'notes' in entry
            assert 'items' in entry

        # 異常系
        with pytest.raises(GeneratorError):
            generator.generate_entries(
                start_date=end_date,  # 開始日が終了日より後
                end_date=start_date
            )

class TestBackup:
    def test_create_backup(self, backup, tmp_path):
        # テスト用のDBファイル作成
        db_path = tmp_path / 'test.db'
        db_path.write_text('test data')

        # 正常系
        metadata = {
            'operation': 'test',
            'timestamp': datetime.now().strftime('%Y/%m/%d %H:%M:%S')
        }
        backup_path = backup.create_backup(str(db_path), metadata)
        assert os.path.exists(backup_path)

        # 異常系
        with pytest.raises(BackupError):
            backup.create_backup('non_existent.db')  # 存在しないファイル

    def test_restore_backup(self, backup, tmp_path):
        # テスト用のバックアップファイル作成
        backup_path = tmp_path / 'backup.db'
        backup_path.write_text('backup data')

        target_path = tmp_path / 'target.db'
        target_path.write_text('original data')

        # 正常系
        backup.restore_backup(str(backup_path), str(target_path))
        assert target_path.read_text() == 'backup data'

        # 異常系
        with pytest.raises(BackupError):
            backup.restore_backup('non_existent.db', str(target_path))

class TestInserter:
    def test_insert_entries(self, inserter, session):
        # テストデータ作成
        entries = [
            {
                'user_id': 'admin',
                'date': '2024/01/01',
                'title': 'テスト1',
                'content': 'テスト内容1',
                'notes': 'テストメモ1',
                'items': []
            },
            {
                'user_id': 'tetsu',
                'date': '2024/01/01',
                'title': 'テスト2',
                'content': 'テスト内容2',
                'notes': 'テストメモ2',
                'items': []
            }
        ]

        # 正常系
        count = inserter.insert_entries(entries)
        assert count == 2

        # 異常系
        with pytest.raises(InsertError):
            inserter.insert_entries([])  # 空のリスト

        with pytest.raises(InsertError):
            inserter.insert_entries([{
                'user_id': 'invalid',  # 存在しないユーザー
                'date': '2024/01/01',
                'title': 'テスト',
                'content': 'テスト内容',
                'notes': 'テストメモ'
            }])

    def test_check_conflicts(self, inserter):
        # テストデータ作成
        entries = [
            {
                'user_id': 'admin',
                'date': '2024/01/01',
                'title': 'テスト1',
                'content': 'テスト内容1',
                'notes': 'テストメモ1'
            }
        ]

        # まずエントリーを挿入
        inserter.insert_entries(entries)

        # 競合チェック
        conflicts = inserter.check_conflicts(entries)
        assert len(conflicts) == 1
        assert conflicts[0]['user_id'] == 'admin'
        assert conflicts[0]['date'] == '2024/01/01'
