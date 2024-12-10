import pytest
from datetime import datetime
from models.entry import Entry
from models.user import User
from models.diary_item import DiaryItem
from database import db
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError

class TestEntry:
    def setup_method(self, method):
        """各テストメソッドの前にデータベースをクリア"""
        with db.session() as session:
            session.execute(text('DELETE FROM diary_items'))
            session.execute(text('DELETE FROM entries'))
            session.execute(text('DELETE FROM users'))
            session.commit()

    def create_test_user(self, app):
        """テスト用のユーザーを作成"""
        with app.app_context():
            user = User(
                userid='testuser',
                name='Test User',
                password='password',
                is_admin=False,
                is_locked=False,
                is_visible=True,
                login_attempts=0,
                created_at=datetime.now()
            )
            db.session.add(user)
            db.session.commit()
            
            # ユーザーを再取得して返す
            return db.session.execute(select(User).filter_by(userid='testuser')).scalar_one()

    def test_entry_init(self, app):
        """__init__メソッドの直接テスト"""
        with app.app_context():
            # 最小限の引数でEntryオブジェクトを作成
            entry = Entry()
            Entry.__init__(
                entry,
                user_id=1,
                title='Test',
                content='Content'
            )
            
            # デフォルト値の確認
            assert entry.notes == ''
            assert entry.created_at is not None
            assert entry.updated_at is None

            # 明示的にnotesを設定しない場合
            entry2 = Entry()
            Entry.__init__(
                entry2,
                user_id=1,
                title='Test 2',
                content='Content 2',
                created_at=datetime.now()
            )
            assert entry2.notes == ''

    def test_entry_creation(self, app):
        """エントリー作成の基本テスト"""
        with app.app_context():
            user = self.create_test_user(app)
            
            # 基本的なエントリーの作成
            entry = Entry(
                user_id=user.id,
                title='Test Entry',
                content='Test Content',
                notes='Test Notes',
                created_at=datetime.now()
            )
            db.session.add(entry)
            db.session.commit()

            # 属性の確認
            assert entry.id is not None
            assert entry.user_id == user.id
            assert entry.title == 'Test Entry'
            assert entry.content == 'Test Content'
            assert entry.notes == 'Test Notes'
            assert entry.created_at is not None
            assert entry.updated_at is None

            # デフォルト値の確認（notesパラメータを完全に省略）
            entry2 = Entry(
                user_id=user.id,
                title='Test Entry 2',
                content='Test Content 2'
            )
            db.session.add(entry2)
            db.session.commit()

            assert entry2.notes == ''
            assert entry2.created_at is not None

            # デフォルト値の確認（notesパラメータにNoneを設定）
            entry3 = Entry(
                user_id=user.id,
                title='Test Entry 3',
                content='Test Content 3',
                notes=None
            )
            db.session.add(entry3)
            db.session.commit()

            assert entry3.notes == ''
            assert entry3.created_at is not None

            # 空のディクショナリからの作成
            kwargs = {}
            kwargs['user_id'] = user.id
            kwargs['title'] = 'Test Entry 4'
            kwargs['content'] = 'Test Content 4'
            entry4 = Entry(**kwargs)
            db.session.add(entry4)
            db.session.commit()

            assert entry4.notes == ''
            assert entry4.created_at is not None

    def test_entry_validation(self, app):
        """エントリーのバリデーションテスト"""
        with app.app_context():
            user = self.create_test_user(app)
            
            # タイトルのバリデーション
            entry = Entry(user_id=user.id, content='Content')
            with pytest.raises(IntegrityError):
                db.session.add(entry)
                db.session.commit()
            db.session.rollback()

            with pytest.raises(ValueError, match='Title must be a string'):
                entry = Entry(
                    user_id=user.id,
                    title=123,
                    content='Content'
                )

            with pytest.raises(ValueError, match='Title cannot be empty'):
                entry = Entry(
                    user_id=user.id,
                    title='',
                    content='Content'
                )

            with pytest.raises(ValueError, match='Title must be 100 characters or less'):
                entry = Entry(
                    user_id=user.id,
                    title='a' * 101,
                    content='Content'
                )

            # コンテンツのバリデーション
            entry = Entry(user_id=user.id, title='Title')
            with pytest.raises(IntegrityError):
                db.session.add(entry)
                db.session.commit()
            db.session.rollback()

            with pytest.raises(ValueError, match='Content must be a string'):
                entry = Entry(
                    user_id=user.id,
                    title='Title',
                    content=123
                )

            with pytest.raises(ValueError, match='Content cannot be empty'):
                entry = Entry(
                    user_id=user.id,
                    title='Title',
                    content=''
                )

            # Noneの値のテスト
            with pytest.raises(ValueError, match='Content cannot be None'):
                entry = Entry(
                    user_id=user.id,
                    title='Title',
                    content=None
                )

            # ノートのバリデーション
            with pytest.raises(ValueError, match='Notes must be a string'):
                entry = Entry(
                    user_id=user.id,
                    title='Title',
                    content='Content',
                    notes=123
                )

            # Noneのノートは空文字列に変換される
            entry = Entry(
                user_id=user.id,
                title='Title',
                content='Content',
                notes=None
            )
            assert entry.notes == ''

            # user_idのバリデーション
            entry = Entry(title='Title', content='Content')
            with pytest.raises(IntegrityError):
                db.session.add(entry)
                db.session.commit()
            db.session.rollback()

            with pytest.raises(ValueError, match='User ID must be an integer'):
                entry = Entry(
                    user_id='invalid',
                    title='Title',
                    content='Content'
                )

            with pytest.raises(ValueError, match='User ID must be positive'):
                entry = Entry(
                    user_id=0,
                    title='Title',
                    content='Content'
                )

            with pytest.raises(ValueError, match='User ID cannot be None'):
                entry = Entry(
                    user_id=None,
                    title='Title',
                    content='Content'
                )

    def test_entry_relationships(self, app):
        """エントリーのリレーションシップテスト"""
        with app.app_context():
            user = self.create_test_user(app)
            
            # エントリーの作成
            entry = Entry(
                user_id=user.id,
                title='Test Entry',
                content='Test Content'
            )
            db.session.add(entry)
            db.session.commit()

            # ユーザーとの関連を確認（オブジェクトを再取得）
            entry = db.session.get(Entry, entry.id)
            user = db.session.get(User, user.id)
            
            assert entry.user.id == user.id
            assert entry.user.userid == user.userid
            assert any(e.id == entry.id for e in user.entries)

            # DiaryItemsの追加
            items = [
                DiaryItem(
                    entry_id=entry.id,
                    item_name=f'Item {i}',
                    item_content=f'Content {i}'
                )
                for i in range(3)
            ]
            db.session.add_all(items)
            db.session.commit()

            # DiaryItemsとの関連を確認
            entry = db.session.get(Entry, entry.id)
            assert len(entry.items) == 3
            for i, item in enumerate(sorted(entry.items, key=lambda x: x.item_name)):
                assert item.item_name == f'Item {i}'
                assert item.entry.id == entry.id

    def test_entry_cascade_delete(self, app):
        """エントリー削除時のカスケード削除テスト"""
        with app.app_context():
            user = self.create_test_user(app)
            
            # エントリーとDiaryItemsの作成
            entry = Entry(
                user_id=user.id,
                title='Test Entry',
                content='Test Content'
            )
            db.session.add(entry)
            db.session.commit()

            items = [
                DiaryItem(
                    entry_id=entry.id,
                    item_name=f'Item {i}',
                    item_content=f'Content {i}'
                )
                for i in range(3)
            ]
            db.session.add_all(items)
            db.session.commit()

            # エントリーを削除
            db.session.delete(entry)
            db.session.commit()

            # DiaryItemsも削除されていることを確認
            remaining_items = db.session.execute(
                select(DiaryItem).filter_by(entry_id=entry.id)
            ).scalars().all()
            assert len(remaining_items) == 0

    def test_entry_update(self, app):
        """エントリーの更新テスト"""
        with app.app_context():
            user = self.create_test_user(app)
            
            # エントリーの作成
            entry = Entry(
                user_id=user.id,
                title='Original Title',
                content='Original Content',
                notes='Original Notes'
            )
            db.session.add(entry)
            db.session.commit()

            original_created_at = entry.created_at

            # 更新前のupdated_atがNoneであることを確認
            assert entry.updated_at is None

            # エントリーの更新
            entry.update(
                title='Updated Title',
                content='Updated Content',
                notes='Updated Notes'
            )
            db.session.commit()

            # 更新された属性を確認
            assert entry.title == 'Updated Title'
            assert entry.content == 'Updated Content'
            assert entry.notes == 'Updated Notes'
            assert entry.created_at == original_created_at
            assert entry.updated_at is not None

    def test_entry_partial_update(self, app):
        """エントリーの部分更新テスト"""
        with app.app_context():
            user = self.create_test_user(app)
            
            # エントリーの作成
            entry = Entry(
                user_id=user.id,
                title='Original Title',
                content='Original Content',
                notes='Original Notes'
            )
            db.session.add(entry)
            db.session.commit()

            # タイトルのみ更新
            entry.update(title='Updated Title')
            db.session.commit()

            assert entry.title == 'Updated Title'
            assert entry.content == 'Original Content'
            assert entry.notes == 'Original Notes'
            assert entry.updated_at is not None

    def test_entry_invalid_update(self, app):
        """無効な更新のテスト"""
        with app.app_context():
            user = self.create_test_user(app)
            
            entry = Entry(
                user_id=user.id,
                title='Original Title',
                content='Original Content'
            )
            db.session.add(entry)
            db.session.commit()

            # 存在しない属性での更新
            entry.update(invalid_field='Invalid Value')
            assert not hasattr(entry, 'invalid_field')

            # バリデーションエラーの確認
            with pytest.raises(ValueError, match='Title cannot be empty'):
                entry.update(title='')
            
            with pytest.raises(ValueError, match='Content must be a string'):
                entry.update(content=123)

    def test_entry_repr(self, app):
        """__repr__メソッドのテスト"""
        with app.app_context():
            user = self.create_test_user(app)
            
            entry = Entry(
                user_id=user.id,
                title='Test Entry',
                content='Test Content'
            )
            assert repr(entry) == '<Entry Test Entry>'

            # 特殊文字を含むタイトル
            entry.title = 'Test/Entry#1'
            assert repr(entry) == '<Entry Test/Entry#1>'

            # 長いタイトル
            entry.title = 'A' * 100
            assert repr(entry) == f'<Entry {"A" * 100}>'
