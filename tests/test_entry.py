import pytest
from datetime import datetime
from models.entry import Entry
from models.user import User
from models.diary_item import DiaryItem
from database import db

class TestEntry:
    def test_entry_creation(self, app, session):
        """エントリーの基本的な作成テスト"""
        # テスト用のユーザーを作成
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

        # created_atとnotesを指定してエントリーを作成
        specified_time = datetime(2024, 1, 1, 12, 0, 0)
        entry = Entry(
            user_id=user.id,
            title='Test Entry',
            content='Test Content',
            notes='Test Notes',
            created_at=specified_time
        )
        session.add(entry)
        session.flush()

        # 基本的な属性を検証
        assert entry.id is not None
        assert entry.user_id == user.id
        assert entry.title == 'Test Entry'
        assert entry.content == 'Test Content'
        assert entry.notes == 'Test Notes'
        assert entry.created_at == specified_time
        assert entry.updated_at is None

        # デフォルト値のテスト（created_atとnotesを指定しない）
        entry2 = Entry(
            user_id=user.id,
            title='Test Entry 2',
            content='Test Content 2'
        )
        session.add(entry2)
        session.flush()

        assert entry2.notes == ''  # デフォルトの空文字列
        assert entry2.created_at is not None
        assert isinstance(entry2.created_at, datetime)
        assert entry2.created_at > specified_time

    def test_entry_relationships(self, app, session):
        """エントリーのリレーションシップテスト"""
        # テスト用のユーザーを作成
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

        # エントリーを作成
        entry = Entry(
            user_id=user.id,
            title='Test Entry',
            content='Test Content',
            notes='Test Notes'
        )
        session.add(entry)
        session.flush()

        # DiaryItemを追加
        diary_item1 = DiaryItem(
            entry_id=entry.id,
            item_name='Test Item 1',
            item_content='Content 1'
        )
        diary_item2 = DiaryItem(
            entry_id=entry.id,
            item_name='Test Item 2',
            item_content='Content 2'
        )
        session.add_all([diary_item1, diary_item2])
        session.flush()

        # リレーションシップを検証
        assert entry.user == user
        assert entry in user.entries
        assert len(entry.items) == 2
        assert diary_item1 in entry.items
        assert diary_item2 in entry.items

        # cascade deleteのテスト
        session.delete(entry)
        session.flush()
        
        # DiaryItemも削除されていることを確認
        assert session.query(DiaryItem).filter_by(id=diary_item1.id).first() is None
        assert session.query(DiaryItem).filter_by(id=diary_item2.id).first() is None

    def test_entry_validation(self, app, session):
        """エントリーのバリデーションテスト"""
        # タイトルの長さ制限テスト
        with pytest.raises(ValueError, match='Title must be 100 characters or less'):
            Entry(
                user_id=1,
                title='a' * 101,  # 100文字を超える
                content='Test Content',
                notes='Test Notes'
            )

        # 必須フィールドの検証
        with pytest.raises(Exception):
            entry = Entry()
            session.add(entry)
            session.flush()

    def test_entry_update(self, app, session):
        """エントリーの更新テスト"""
        # エントリーを作成
        entry = Entry(
            user_id=1,
            title='Original Title',
            content='Original Content',
            notes='Original Notes'
        )
        session.add(entry)
        session.flush()

        original_created_at = entry.created_at

        # 更新前のupdated_atを確認
        assert entry.updated_at is None

        # エントリーを更新
        entry.update(
            title='Updated Title',
            content='Updated Content',
            notes='Updated Notes'
        )
        session.flush()

        # 更新後の状態を検証
        assert entry.title == 'Updated Title'
        assert entry.content == 'Updated Content'
        assert entry.notes == 'Updated Notes'
        assert entry.created_at == original_created_at
        assert entry.updated_at is not None
        assert isinstance(entry.updated_at, datetime)

        # 存在しない属性は無視されることを確認
        entry.update(
            non_existent_field='Some Value',
            another_field=123
        )
        assert not hasattr(entry, 'non_existent_field')
        assert not hasattr(entry, 'another_field')

        # 部分的な更新
        current_title = entry.title
        current_content = entry.content
        previous_update = entry.updated_at

        entry.update(notes='Only Notes Updated')
        session.flush()

        assert entry.title == current_title
        assert entry.content == current_content
        assert entry.notes == 'Only Notes Updated'
        assert entry.updated_at > previous_update

    def test_entry_repr(self, app, session):
        """エントリーの__repr__メソッドのテスト"""
        # 通常のケース
        entry = Entry(
            user_id=1,
            title='Test Entry',
            content='Test Content',
            notes='Test Notes'
        )
        assert repr(entry) == '<Entry Test Entry>'

        # 特殊文字を含むケース
        entry2 = Entry(
            user_id=1,
            title='Test/Entry#2',
            content='Test Content',
            notes='Test Notes'
        )
        assert repr(entry2) == '<Entry Test/Entry#2>'

        # 長いタイトルのケース
        long_title = 'A' * 100
        entry3 = Entry(
            user_id=1,
            title=long_title,
            content='Test Content',
            notes='Test Notes'
        )
        assert repr(entry3) == f'<Entry {long_title}>'

        # 空のタイトルのケース（バリデーションで防ぐべきだが、__repr__は対応する必要がある）
        entry4 = Entry(
            user_id=1,
            title='',
            content='Test Content',
            notes='Test Notes'
        )
        assert repr(entry4) == '<Entry >'
