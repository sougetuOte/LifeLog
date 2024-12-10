import pytest
from datetime import datetime
from models.diary_item import DiaryItem
from models.entry import Entry
from models.user import User
from database import db
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, ForeignKeyViolation

class TestDiaryItem:
    def setup_method(self):
        """各テストメソッドの前にデータベースをクリアし、テストデータを作成"""
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

            # テストエントリーを作成
            self.entry = Entry(
                user=self.user,
                title='Test Entry',
                content='Test Content',
                created_at=datetime.now()
            )
            session.add(self.entry)
            session.commit()

            self.entry_id = self.entry.id

    def teardown_method(self):
        """各テストメソッドの後にデータベースをクリア"""
        with db.session() as session:
            session.query(DiaryItem).delete()
            session.query(Entry).delete()
            session.query(User).delete()
            session.commit()

    def test_create_diary_item_with_valid_data(self, app):
        """有効なデータでのDiaryItem作成テスト"""
        with app.app_context():
            item = DiaryItem(
                entry_id=self.entry_id,
                item_name='Test Item',
                item_content='Test Item Content'
            )
            assert item.entry_id == self.entry_id
            assert item.item_name == 'Test Item'
            assert item.item_content == 'Test Item Content'
            assert isinstance(item.created_at, datetime)

    def test_create_diary_item_with_entry_object(self, app):
        """Entryオブジェクトを使用したDiaryItem作成テスト"""
        with app.app_context():
            with db.session() as session:
                entry = session.get(Entry, self.entry_id)
                item = DiaryItem(
                    entry=entry,
                    item_name='Test Item',
                    item_content='Test Item Content'
                )
                assert item.entry_id == self.entry_id
                assert item.entry == entry

    def test_create_diary_item_without_required_fields(self, app):
        """必須フィールドなしでのDiaryItem作成テスト"""
        with app.app_context():
            # entry_idなし
            with pytest.raises(ValueError, match='Entry ID cannot be None'):
                DiaryItem(
                    item_name='Test Item',
                    item_content='Test Item Content'
                )

            # item_nameなし
            with pytest.raises(ValueError, match='Item name cannot be None'):
                DiaryItem(
                    entry_id=self.entry_id,
                    item_content='Test Item Content'
                )

            # item_contentなし
            with pytest.raises(ValueError, match='Item content cannot be None'):
                DiaryItem(
                    entry_id=self.entry_id,
                    item_name='Test Item'
                )

    def test_validate_entry_id(self, app):
        """entry_idのバリデーションテスト"""
        with app.app_context():
            # Noneの場合
            with pytest.raises(ValueError, match='Entry ID cannot be None'):
                DiaryItem(
                    entry_id=None,
                    item_name='Test Item',
                    item_content='Test Content'
                )

            # 文字列の場合
            with pytest.raises(ValueError, match='Entry ID must be an integer'):
                DiaryItem(
                    entry_id='1',
                    item_name='Test Item',
                    item_content='Test Content'
                )

            # 負数の場合
            with pytest.raises(ValueError, match='Entry ID must be a positive integer'):
                DiaryItem(
                    entry_id=-1,
                    item_name='Test Item',
                    item_content='Test Content'
                )

            # 0の場合
            with pytest.raises(ValueError, match='Entry ID must be a positive integer'):
                DiaryItem(
                    entry_id=0,
                    item_name='Test Item',
                    item_content='Test Content'
                )

    def test_validate_item_name(self, app):
        """item_nameのバリデーションテスト"""
        with app.app_context():
            # Noneの場合
            with pytest.raises(ValueError, match='Item name cannot be None'):
                DiaryItem(
                    entry_id=self.entry_id,
                    item_name=None,
                    item_content='Test Content'
                )

            # 数値の場合
            with pytest.raises(ValueError, match='Item name must be a string'):
                DiaryItem(
                    entry_id=self.entry_id,
                    item_name=123,
                    item_content='Test Content'
                )

            # 空文字の場合
            with pytest.raises(ValueError, match='Item name cannot be empty'):
                DiaryItem(
                    entry_id=self.entry_id,
                    item_name='',
                    item_content='Test Content'
                )

            # スペースのみの場合
            with pytest.raises(ValueError, match='Item name cannot be empty'):
                DiaryItem(
                    entry_id=self.entry_id,
                    item_name='   ',
                    item_content='Test Content'
                )

            # 100文字を超える場合
            with pytest.raises(ValueError, match='Item name must be 100 characters or less'):
                DiaryItem(
                    entry_id=self.entry_id,
                    item_name='a' * 101,
                    item_content='Test Content'
                )

    def test_validate_item_content(self, app):
        """item_contentのバリデーションテスト"""
        with app.app_context():
            # Noneの場合
            with pytest.raises(ValueError, match='Item content cannot be None'):
                DiaryItem(
                    entry_id=self.entry_id,
                    item_name='Test Item',
                    item_content=None
                )

            # 数値の場合
            with pytest.raises(ValueError, match='Item content must be a string'):
                DiaryItem(
                    entry_id=self.entry_id,
                    item_name='Test Item',
                    item_content=123
                )

            # 空文字の場合
            with pytest.raises(ValueError, match='Item content cannot be empty'):
                DiaryItem(
                    entry_id=self.entry_id,
                    item_name='Test Item',
                    item_content=''
                )

            # スペースのみの場合
            with pytest.raises(ValueError, match='Item content cannot be empty'):
                DiaryItem(
                    entry_id=self.entry_id,
                    item_name='Test Item',
                    item_content='   '
                )

    def test_relationship(self, app):
        """リレーションシップのテスト"""
        with app.app_context():
            with db.session() as session:
                # DiaryItemを作成して保存
                item = DiaryItem(
                    entry_id=self.entry_id,
                    item_name='Test Item',
                    item_content='Test Content'
                )
                session.add(item)
                session.commit()

                # リレーションシップを確認
                entry = session.get(Entry, self.entry_id)
                assert item.entry == entry
                assert item in entry.items

    def test_repr(self, app):
        """__repr__メソッドのテスト"""
        with app.app_context():
            item = DiaryItem(
                entry_id=self.entry_id,
                item_name='Test Item',
                item_content='Test Content'
            )
            assert repr(item) == '<DiaryItem Test Item>'

    def test_bulk_diary_items_creation(self, app):
        """複数のDiaryItemの一括作成テスト"""
        with app.app_context():
            with db.session() as session:
                # 複数のDiaryItemを作成
                items = [
                    DiaryItem(
                        entry_id=self.entry_id,
                        item_name=f'Item {i}',
                        item_content=f'Content {i}'
                    )
                    for i in range(1, 4)
                ]
                session.add_all(items)
                session.commit()

                # 保存されたアイテムを確認
                saved_items = session.execute(
                    select(DiaryItem).filter_by(entry_id=self.entry_id)
                ).scalars().all()
                assert len(saved_items) == 3
                assert all(isinstance(item.created_at, datetime) for item in saved_items)
                assert all(item.entry_id == self.entry_id for item in saved_items)

    def test_diary_item_update(self, app):
        """DiaryItemの更新テスト"""
        with app.app_context():
            with db.session() as session:
                # アイテムを作成
                item = DiaryItem(
                    entry_id=self.entry_id,
                    item_name='Original Name',
                    item_content='Original Content'
                )
                session.add(item)
                session.commit()
                item_id = item.id

                # アイテムを更新
                item.item_name = 'Updated Name'
                item.item_content = 'Updated Content'
                session.commit()

                # 更新を確認
                updated_item = session.get(DiaryItem, item_id)
                assert updated_item.item_name == 'Updated Name'
                assert updated_item.item_content == 'Updated Content'

    def test_diary_item_cascade_delete(self, app):
        """DiaryItemのカスケード削除テスト"""
        with app.app_context():
            with db.session() as session:
                # アイテムを作成
                items = [
                    DiaryItem(
                        entry_id=self.entry_id,
                        item_name=f'Item {i}',
                        item_content=f'Content {i}'
                    )
                    for i in range(1, 4)
                ]
                session.add_all(items)
                session.commit()

                # エントリーを削除
                entry = session.get(Entry, self.entry_id)
                session.delete(entry)
                session.commit()

                # アイテムも削除されていることを確認
                remaining_items = session.execute(
                    select(DiaryItem).filter_by(entry_id=self.entry_id)
                ).scalars().all()
                assert len(remaining_items) == 0

    def test_diary_item_timestamps(self, app):
        """タイムスタンプの自動設定テスト"""
        with app.app_context():
            # created_atを指定せずに作成
            item1 = DiaryItem(
                entry_id=self.entry_id,
                item_name='Item 1',
                item_content='Content 1'
            )
            assert isinstance(item1.created_at, datetime)
            before = datetime.now()
            
            with db.session() as session:
                session.add(item1)
                session.commit()
                after = datetime.now()
                
                # タイムスタンプが適切な範囲内にあることを確認
                assert before <= item1.created_at <= after

            # created_atを指定して作成
            specific_time = datetime(2023, 1, 1, 12, 0, 0)
            item2 = DiaryItem(
                entry_id=self.entry_id,
                item_name='Item 2',
                item_content='Content 2',
                created_at=specific_time
            )
            assert item2.created_at == specific_time


    def test_diary_item_with_nonexistent_entry(self, app):
        """存在しないEntryへの参照テスト"""
        with app.app_context():
            with db.session() as session:
                # 存在しないentry_idを使用
                item = DiaryItem(
                    entry_id=9999,  # 存在しないID
                    item_name='Test Item',
                    item_content='Test Content'
                )
                session.add(item)
                
                # データベースに保存しようとすると外部キー制約違反
                with pytest.raises(IntegrityError):
                    session.commit()
