import pytest
from datetime import datetime
from models.diary_item import DiaryItem
from models.entry import Entry
from models.user import User
from database import db

class TestDiaryItem:
    def test_diary_item_creation(self, app, session):
        """DiaryItemの基本的な作成テスト"""
        # テスト用のユーザーとエントリーを作成
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
        diary_item2 = DiaryItem(
            entry_id=entry.id,
            item_name='Test Item 2',
            item_content='Test Item Content 2'
        )
        session.add(diary_item2)
        session.flush()

        # デフォルトのcreated_atが設定されていることを確認
        assert diary_item2.created_at is not None
        assert isinstance(diary_item2.created_at, datetime)
        assert diary_item2.created_at > specified_time

    def test_diary_item_relationships(self, app, session):
        """DiaryItemのリレーションシップテスト"""
        # テスト用のユーザーとエントリーを作成
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

    def test_diary_item_validation(self, app, session):
        """DiaryItemのバリデーションテスト"""
        # 必須フィールドの検証
        with pytest.raises(Exception):
            diary_item = DiaryItem()
            session.add(diary_item)
            session.flush()

        # item_nameの長さ制限テスト
        with pytest.raises(Exception):
            diary_item = DiaryItem(
                entry_id=1,
                item_name='a' * 101,  # 100文字を超える
                item_content='Test Content'
            )
            session.add(diary_item)
            session.flush()

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

        # 空の名前のケース（バリデーションで防ぐべきだが、__repr__は対応する必要がある）
        diary_item4 = DiaryItem(
            entry_id=1,
            item_name='',
            item_content='Test Content'
        )
        assert repr(diary_item4) == '<DiaryItem >'

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
        diary_item2 = DiaryItem(
            entry_id=1,
            item_name='Test Item 2',
            item_content='Test Content 2'
        )
        assert diary_item2.created_at is not None
        assert isinstance(diary_item2.created_at, datetime)
        assert diary_item2.created_at > specified_time

        # タイムスタンプの上書き防止
        diary_item2.created_at = specified_time
        new_time = datetime(2024, 1, 2, 12, 0, 0)
        diary_item2.created_at = new_time
        assert diary_item2.created_at == new_time
