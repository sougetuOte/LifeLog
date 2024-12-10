import pytest
from datetime import datetime
from models.entry import Entry
from models.user import User
from models.diary_item import DiaryItem
from database import db

class TestEntry:
    def setup_method(self):
        """各テストメソッドの前にデータベースをクリアし、テストユーザーを作成"""
        with db.session() as session:
            # テストユーザーを作成
            self.user = User(
                userid='test_user',
                name='Test User',
                password='TestPass123',
                created_at=datetime.now()
            )
            session.add(self.user)
            session.commit()
            self.user_id = self.user.id

    def teardown_method(self):
        """各テストメソッドの後にデータベースをクリア"""
        with db.session() as session:
            session.query(DiaryItem).delete()
            session.query(Entry).delete()
            session.query(User).delete()
            session.commit()

    def test_create_entry_with_valid_data(self, app):
        """有効なデータでのEntry作成テスト"""
        with app.app_context():
            entry = Entry(
                user_id=self.user_id,
                title='Test Entry',
                content='Test Content'
            )
            assert entry.user_id == self.user_id
            assert entry.title == 'Test Entry'
            assert entry.content == 'Test Content'
            assert entry.notes == ''  # デフォルト値
            assert isinstance(entry.created_at, datetime)
            assert entry.updated_at is None

    def test_create_entry_with_all_fields(self, app):
        """全フィールドを指定したEntry作成テスト"""
        with app.app_context():
            now = datetime.now()
            entry = Entry(
                user_id=self.user_id,
                title='Test Entry',
                content='Test Content',
                notes='Test Notes',
                created_at=now
            )
            assert entry.notes == 'Test Notes'
            assert entry.created_at == now

    def test_validate_title(self, app):
        """titleのバリデーションテスト"""
        with app.app_context():
            # Noneの場合
            with pytest.raises(ValueError, match='Title cannot be None'):
                Entry(
                    user_id=self.user_id,
                    title=None,
                    content='Test Content'
                )

            # 数値の場合
            with pytest.raises(ValueError, match='Title must be a string'):
                Entry(
                    user_id=self.user_id,
                    title=123,
                    content='Test Content'
                )

            # 空文字の場合
            with pytest.raises(ValueError, match='Title cannot be empty'):
                Entry(
                    user_id=self.user_id,
                    title='',
                    content='Test Content'
                )

            # スペースのみの場合
            with pytest.raises(ValueError, match='Title cannot be empty'):
                Entry(
                    user_id=self.user_id,
                    title='   ',
                    content='Test Content'
                )

            # 100文字を超える場合
            with pytest.raises(ValueError, match='Title must be 100 characters or less'):
                Entry(
                    user_id=self.user_id,
                    title='a' * 101,
                    content='Test Content'
                )

    def test_validate_content(self, app):
        """contentのバリデーションテスト"""
        with app.app_context():
            # Noneの場合
            with pytest.raises(ValueError, match='Content cannot be None'):
                Entry(
                    user_id=self.user_id,
                    title='Test Title',
                    content=None
                )

            # 数値の場合
            with pytest.raises(ValueError, match='Content must be a string'):
                Entry(
                    user_id=self.user_id,
                    title='Test Title',
                    content=123
                )

            # 空文字の場合
            with pytest.raises(ValueError, match='Content cannot be empty'):
                Entry(
                    user_id=self.user_id,
                    title='Test Title',
                    content=''
                )

            # スペースのみの場合
            with pytest.raises(ValueError, match='Content cannot be empty'):
                Entry(
                    user_id=self.user_id,
                    title='Test Title',
                    content='   '
                )

    def test_validate_notes(self, app):
        """notesのバリデーションテスト"""
        with app.app_context():
            # Noneの場合（空文字に変換される）
            entry = Entry(
                user_id=self.user_id,
                title='Test Title',
                content='Test Content',
                notes=None
            )
            assert entry.notes == ''

            # 数値の場合
            with pytest.raises(ValueError, match='Notes must be a string'):
                Entry(
                    user_id=self.user_id,
                    title='Test Title',
                    content='Test Content',
                    notes=123
                )

    def test_validate_user_id(self, app):
        """user_idのバリデーションテスト"""
        with app.app_context():
            # Noneの場合
            with pytest.raises(ValueError, match='User ID cannot be None'):
                Entry(
                    user_id=None,
                    title='Test Title',
                    content='Test Content'
                )

            # 文字列の場合
            with pytest.raises(ValueError, match='User ID must be an integer'):
                Entry(
                    user_id='1',
                    title='Test Title',
                    content='Test Content'
                )

            # 負数の場合
            with pytest.raises(ValueError, match='User ID must be positive'):
                Entry(
                    user_id=-1,
                    title='Test Title',
                    content='Test Content'
                )

            # 0の場合
            with pytest.raises(ValueError, match='User ID must be positive'):
                Entry(
                    user_id=0,
                    title='Test Title',
                    content='Test Content'
                )

    def test_relationship_with_user(self, app):
        """Userとのリレーションシップテスト"""
        with app.app_context():
            with db.session() as session:
                entry = Entry(
                    user_id=self.user_id,
                    title='Test Entry',
                    content='Test Content'
                )
                session.add(entry)
                session.commit()

                # リレーションシップを確認
                user = session.get(User, self.user_id)
                assert entry.user == user
                assert entry in user.entries

    def test_relationship_with_diary_items(self, app):
        """DiaryItemsとのリレーションシップテスト"""
        with app.app_context():
            with db.session() as session:
                # エントリーを作成
                entry = Entry(
                    user_id=self.user_id,
                    title='Test Entry',
                    content='Test Content'
                )
                session.add(entry)
                session.commit()

                # DiaryItemを追加
                item1 = DiaryItem(
                    entry_id=entry.id,
                    item_name='Item 1',
                    item_content='Content 1'
                )
                item2 = DiaryItem(
                    entry_id=entry.id,
                    item_name='Item 2',
                    item_content='Content 2'
                )
                session.add(item1)
                session.add(item2)
                session.commit()

                # リレーションシップを確認
                assert len(entry.items) == 2
                assert item1 in entry.items
                assert item2 in entry.items

                # cascade deleteのテスト
                session.delete(entry)
                session.commit()

                # DiaryItemsも削除されていることを確認
                items = session.query(DiaryItem).all()
                assert len(items) == 0

    def test_update(self, app):
        """updateメソッドのテスト"""
        with app.app_context():
            with db.session() as session:
                # エントリーを作成
                entry = Entry(
                    user_id=self.user_id,
                    title='Original Title',
                    content='Original Content',
                    notes='Original Notes'
                )
                session.add(entry)
                session.commit()

                # 更新前のupdated_atを記録
                assert entry.updated_at is None

                # 更新を実行
                entry.update(
                    title='Updated Title',
                    content='Updated Content',
                    notes='Updated Notes'
                )

                # 変更を確認
                assert entry.title == 'Updated Title'
                assert entry.content == 'Updated Content'
                assert entry.notes == 'Updated Notes'
                assert isinstance(entry.updated_at, datetime)

                # 存在しない属性は無視される
                entry.update(nonexistent_field='value')
                assert not hasattr(entry, 'nonexistent_field')

    def test_repr(self, app):
        """__repr__メソッドのテスト"""
        with app.app_context():
            entry = Entry(
                user_id=self.user_id,
                title='Test Entry',
                content='Test Content'
            )
            assert repr(entry) == '<Entry Test Entry>'
