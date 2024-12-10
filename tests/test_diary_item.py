import pytest
from datetime import datetime, timedelta
from models.diary_item import DiaryItem
from models.entry import Entry
from models.user import User
from database import db
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy import text

class TestDiaryItem:
    def setup_user_and_entry(self, session):
        """テスト用のユーザーとエントリーをセットアップ"""
        user = User(
            userid='test_user',
            name='Test User',
            password='password',
            is_admin=False,
            is_locked=False,
            is_visible=True,
            login_attempts=0,
            created_at=datetime.now()
        )
        session.add(user)
        session.flush()

        entry = Entry(
            user_id=user.id,
            title='Test Entry',
            content='Test Content',
            notes='Test Notes',
            created_at=datetime.now()
        )
        session.add(entry)
        session.flush()
        return user, entry

    def test_diary_item_creation(self, app, session):
        """DiaryItemの基本的な作成テスト"""
        # テスト用のユーザーとエントリーを作成
        user, entry = self.setup_user_and_entry(session)

        # created_atを指定してDiaryItemを作成
        specified_time = datetime(2024, 1, 1, 12, 0, 0)
        diary_item = DiaryItem(
            entry_id=entry.id,
            item_name='Test Item',
            item_content='Test Item Content',
            created_at=specified_time
        )
        session.add(diary_item)
        session.flush()

        # 基本的な属性を検証
        assert diary_item.id is not None
        assert diary_item.entry_id == entry.id
        assert diary_item.item_name == 'Test Item'
        assert diary_item.item_content == 'Test Item Content'
        assert diary_item.created_at == specified_time

        # created_atを指定せずにDiaryItemを作成
        before_creation = datetime.now()
        diary_item2 = DiaryItem(
            entry_id=entry.id,
            item_name='Test Item 2',
            item_content='Test Item Content 2'
        )
        session.add(diary_item2)
        session.flush()
        after_creation = datetime.now()

        # デフォルトのcreated_atが適切な範囲内にあることを確認
        assert diary_item2.created_at is not None
        assert isinstance(diary_item2.created_at, datetime)
        assert before_creation <= diary_item2.created_at <= after_creation

    def test_diary_item_validation(self, app, session):
        """DiaryItemのバリデーションテスト"""
        user, entry = self.setup_user_and_entry(session)

        # entry_idのバリデーション
        with pytest.raises(ValueError, match='Entry ID cannot be None'):
            DiaryItem(item_name='Test', item_content='Content')

        with pytest.raises(ValueError, match='Entry ID must be an integer'):
            DiaryItem(entry_id='invalid', item_name='Test', item_content='Content')

        with pytest.raises(ValueError, match='Entry ID must be a positive integer'):
            DiaryItem(entry_id=0, item_name='Test', item_content='Content')

        with pytest.raises(ValueError, match='Entry ID must be a positive integer'):
            DiaryItem(entry_id=-1, item_name='Test', item_content='Content')

        # item_nameのバリデーション
        with pytest.raises(ValueError, match='Item name cannot be None'):
            DiaryItem(entry_id=entry.id, item_content='Content')

        with pytest.raises(ValueError, match='Item name must be a string'):
            DiaryItem(entry_id=entry.id, item_name=123, item_content='Content')

        with pytest.raises(ValueError, match='Item name cannot be empty'):
            DiaryItem(entry_id=entry.id, item_name='', item_content='Content')

        with pytest.raises(ValueError, match='Item name must be 100 characters or less'):
            DiaryItem(entry_id=entry.id, item_name='a' * 101, item_content='Content')

        # item_contentのバリデーション
        with pytest.raises(ValueError, match='Item content cannot be None'):
            DiaryItem(entry_id=entry.id, item_name='Test')

        with pytest.raises(ValueError, match='Item content must be a string'):
            DiaryItem(entry_id=entry.id, item_name='Test', item_content=123)

        with pytest.raises(ValueError, match='Item content cannot be empty'):
            DiaryItem(entry_id=entry.id, item_name='Test', item_content='')

    def test_diary_item_relationships(self, app, session):
        """DiaryItemのリレーションシップテスト"""
        # テスト用のユーザーとエントリーを作成
        user, entry = self.setup_user_and_entry(session)

        # DiaryItemを作成
        diary_item = DiaryItem(
            entry_id=entry.id,
            item_name='Test Item',
            item_content='Test Item Content'
        )
        session.add(diary_item)
        session.flush()

        # リレーションシップを検証
        assert diary_item.entry == entry
        assert diary_item in entry.items

    def test_diary_item_invalid_entry(self, app, session):
        """存在しないエントリーIDでのDiaryItem作成テスト"""
        # 外部キー制約を有効化
        session.execute(text('PRAGMA foreign_keys = ON'))
        
        # 存在しないエントリーIDでの作成を試みる
        with pytest.raises(IntegrityError):
            invalid_diary_item = DiaryItem(
                entry_id=9999,  # 存在しないID
                item_name='Invalid Item',
                item_content='Invalid Content'
            )
            session.add(invalid_diary_item)
            session.flush()
        session.rollback()

    def test_diary_item_missing_required_fields(self, app, session):
        """必須フィールド欠落のテスト"""
        with pytest.raises(ValueError):
            diary_item = DiaryItem()
            session.add(diary_item)
            session.flush()
        session.rollback()

    def test_diary_item_null_fields(self, app, session):
        """NULL値が許可されていないフィールドのテスト"""
        test_cases = [
            {'entry_id': None, 'item_name': 'Test', 'item_content': 'Content'},
            {'entry_id': 1, 'item_name': None, 'item_content': 'Content'},
            {'entry_id': 1, 'item_name': 'Test', 'item_content': None},
        ]

        for test_case in test_cases:
            with pytest.raises(ValueError):
                diary_item = DiaryItem(**test_case)
                session.add(diary_item)
                session.flush()
            session.rollback()

    def test_diary_item_database_error(self, app, session):
        """DiaryItemのデータベースエラーハンドリングテスト"""
        user, entry = self.setup_user_and_entry(session)

        diary_item = DiaryItem(
            entry_id=entry.id,
            item_name='Test Item',
            item_content='Test Content'
        )
        session.add(diary_item)

        def mock_commit_error(*args, **kwargs):
            if session.is_active:
                session.rollback()
            raise SQLAlchemyError("Database error")

        # db.sessionのcommitをモック化
        original_commit = session.commit
        session.commit = mock_commit_error

        try:
            with pytest.raises(SQLAlchemyError):
                session.commit()
        finally:
            session.commit = original_commit

    def test_diary_item_repr(self, app, session):
        """DiaryItemの__repr__メソッドのテスト"""
        # 通常のケース
        diary_item = DiaryItem(
            entry_id=1,
            item_name='Test Item',
            item_content='Test Content'
        )
        assert repr(diary_item) == '<DiaryItem Test Item>'

        # 特殊文字を含むケース
        diary_item2 = DiaryItem(
            entry_id=1,
            item_name='Test/Item#2',
            item_content='Test Content'
        )
        assert repr(diary_item2) == '<DiaryItem Test/Item#2>'

        # 長い名前のケース
        long_name = 'A' * 100
        diary_item3 = DiaryItem(
            entry_id=1,
            item_name=long_name,
            item_content='Test Content'
        )
        assert repr(diary_item3) == f'<DiaryItem {long_name}>'

    def test_diary_item_timestamps(self, app, session):
        """DiaryItemのタイムスタンプ処理テスト"""
        # 明示的なタイムスタンプ指定
        specified_time = datetime(2024, 1, 1, 12, 0, 0)
        diary_item1 = DiaryItem(
            entry_id=1,
            item_name='Test Item 1',
            item_content='Test Content 1',
            created_at=specified_time
        )
        assert diary_item1.created_at == specified_time

        # デフォルトのタイムスタンプ
        before_creation = datetime.now()
        diary_item2 = DiaryItem(
            entry_id=1,
            item_name='Test Item 2',
            item_content='Test Content 2'
        )
        after_creation = datetime.now()

        assert diary_item2.created_at is not None
        assert isinstance(diary_item2.created_at, datetime)
        assert before_creation <= diary_item2.created_at <= after_creation

        # タイムスタンプの更新テスト
        original_time = diary_item2.created_at
        new_time = datetime.now() + timedelta(days=1)
        diary_item2.created_at = new_time
        assert diary_item2.created_at == new_time
        assert diary_item2.created_at != original_time

    def test_whitespace_validation(self, app, session):
        """空白文字のみの項目名と内容のバリデーションテスト"""
        user, entry = self.setup_user_and_entry(session)

        # 空白文字のみの項目名
        with pytest.raises(ValueError, match='Item name cannot be empty'):
            DiaryItem(
                entry_id=entry.id,
                item_name='   ',
                item_content='Valid Content'
            )

        # 空白文字のみの内容
        with pytest.raises(ValueError, match='Item content cannot be empty'):
            DiaryItem(
                entry_id=entry.id,
                item_name='Valid Name',
                item_content='   '
            )

        # タブや改行のみの項目名
        with pytest.raises(ValueError, match='Item name cannot be empty'):
            DiaryItem(
                entry_id=entry.id,
                item_name='\t\n',
                item_content='Valid Content'
            )

    def test_entry_object_initialization(self, app, session):
        """Entryオブジェクトを直接渡した場合の初期化テスト"""
        user, entry = self.setup_user_and_entry(session)

        # Entryオブジェクトを直接渡してDiaryItemを作成
        diary_item = DiaryItem(
            entry=entry,
            item_name='Test Item',
            item_content='Test Content'
        )
        session.add(diary_item)
        session.flush()

        # entry_idが正しく設定されていることを確認
        assert diary_item.entry_id == entry.id
        assert diary_item.entry == entry

    def test_multiple_items_per_entry(self, app, session):
        """同じEntryに複数のDiaryItemを関連付けるテスト"""
        user, entry = self.setup_user_and_entry(session)

        # 複数のDiaryItemを作成
        items = []
        for i in range(5):
            item = DiaryItem(
                entry_id=entry.id,
                item_name=f'Item {i}',
                item_content=f'Content {i}'
            )
            items.append(item)
            session.add(item)
        session.flush()

        # 全てのアイテムが正しく関連付けられていることを確認
        assert len(entry.items) == 5
        for i, item in enumerate(items):
            assert item in entry.items
            assert item.entry == entry
            assert item.item_name == f'Item {i}'
            assert item.item_content == f'Content {i}'

        # アイテムの順序が作成順を維持していることを確認
        for i in range(len(items) - 1):
            assert items[i].created_at <= items[i + 1].created_at
