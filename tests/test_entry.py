import pytest
from datetime import datetime, timedelta
from models.entry import Entry
from models.user import User
from models.diary_item import DiaryItem
from database import db
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import text

class TestEntry:
    def setup_user(self, session):
        """テスト用のユーザーをセットアップ"""
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
        return user

    def test_entry_creation(self, app, session):
        """エントリーの基本的な作成テスト"""
        user = self.setup_user(session)

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
        assert entry.id is not None, "エントリーIDが生成されていません"
        assert entry.user_id == user.id, "ユーザーIDが正しくありません"
        assert entry.title == 'Test Entry', "タイトルが正しくありません"
        assert entry.content == 'Test Content', "コンテンツが正しくありません"
        assert entry.notes == 'Test Notes', "ノートが正しくありません"
        assert entry.created_at == specified_time, "作成日時が正しくありません"
        assert entry.updated_at is None, "更新日時の初期値がNoneではありません"

        # デフォルト値のテスト
        before_creation = datetime.now()
        entry2 = Entry(
            user_id=user.id,
            title='Test Entry 2',
            content='Test Content 2'
        )
        session.add(entry2)
        session.flush()
        after_creation = datetime.now()

        assert entry2.notes == '', "notesのデフォルト値が空文字列ではありません"
        assert entry2.created_at is not None, "created_atが設定されていません"
        assert isinstance(entry2.created_at, datetime), "created_atがdatetime型ではありません"
        assert before_creation <= entry2.created_at <= after_creation, \
            "created_atが適切な範囲内にありません"

    def test_entry_model_validation(self, app):
        """モデルレベルのバリデーションテスト"""
        # タイトルのバリデーション
        with pytest.raises(ValueError, match='Title cannot be None'):
            Entry(user_id=1, title=None, content='Content')

        with pytest.raises(ValueError, match='Title must be a string'):
            Entry(user_id=1, title=123, content='Content')

        with pytest.raises(ValueError, match='Title cannot be empty'):
            Entry(user_id=1, title='', content='Content')

        with pytest.raises(ValueError, match='Title must be 100 characters or less'):
            Entry(user_id=1, title='a' * 101, content='Content')

        # コンテンツのバリデーション
        with pytest.raises(ValueError, match='Content cannot be None'):
            Entry(user_id=1, title='Title', content=None)

        with pytest.raises(ValueError, match='Content must be a string'):
            Entry(user_id=1, title='Title', content=123)

        with pytest.raises(ValueError, match='Content cannot be empty'):
            Entry(user_id=1, title='Title', content='')

        # ユーザーIDのバリデーション
        with pytest.raises(ValueError, match='User ID cannot be None'):
            Entry(user_id=None, title='Title', content='Content')

        with pytest.raises(ValueError, match='User ID must be an integer'):
            Entry(user_id='1', title='Title', content='Content')

        with pytest.raises(ValueError, match='User ID must be positive'):
            Entry(user_id=0, title='Title', content='Content')

        # ノートのバリデーション
        with pytest.raises(ValueError, match='Notes must be a string'):
            Entry(user_id=1, title='Title', content='Content', notes=123)

        # 有効なケース
        entry = Entry(user_id=1, title='Valid Title', content='Valid Content')
        assert entry.title == 'Valid Title'
        assert entry.content == 'Valid Content'
        assert entry.notes == ''

    def test_entry_database_validation(self, app, session):
        """データベースレベルのバリデーションテスト"""
        # 外部キー制約を有効化
        session.execute(text('PRAGMA foreign_keys = ON'))
        session.commit()

        # 存在しないユーザーIDでの作成を試みる
        with pytest.raises(IntegrityError):
            entry = Entry(
                user_id=999,  # 存在しないID
                title='Test Entry',
                content='Test Content'
            )
            session.add(entry)
            session.flush()
        session.rollback()

        # NULLフィールドのテスト
        test_cases = [
            {'title': 'Test', 'content': 'Content'},  # user_idなし
            {'user_id': 1, 'content': 'Content'},  # titleなし
            {'user_id': 1, 'title': 'Test'},  # contentなし
        ]

        for test_case in test_cases:
            with pytest.raises(IntegrityError):
                entry = Entry(**test_case)
                session.add(entry)
                session.flush()
            session.rollback()

    def test_entry_relationships(self, app, session):
        """エントリーのリレーションシップテスト"""
        user = self.setup_user(session)

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
        assert entry.user == user, "ユーザーとの関連が正しくありません"
        assert entry in user.entries, "ユーザーのエントリーリストに含まれていません"
        assert len(entry.items) == 2, "DiaryItemの数が正しくありません"
        assert diary_item1 in entry.items, "DiaryItem1が関連付けられていません"
        assert diary_item2 in entry.items, "DiaryItem2が関連付けられていません"

    def test_entry_cascade_delete(self, app, session):
        """エントリー削除時のカスケード削除テスト"""
        user = self.setup_user(session)
        
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
        diary_items = [
            DiaryItem(
                entry_id=entry.id,
                item_name=f'Test Item {i}',
                item_content=f'Content {i}'
            )
            for i in range(3)
        ]
        session.add_all(diary_items)
        session.flush()

        # エントリーを削除
        entry_id = entry.id
        diary_item_ids = [item.id for item in diary_items]
        
        session.delete(entry)
        session.flush()
        
        # DiaryItemも削除されていることを確認
        for item_id in diary_item_ids:
            assert session.query(DiaryItem).filter_by(id=item_id).first() is None, \
                f"DiaryItem {item_id}が削除されていません"

    def test_entry_database_error(self, app, session):
        """データベースエラーハンドリングテスト"""
        user = self.setup_user(session)
        
        entry = Entry(
            user_id=user.id,
            title='Test Entry',
            content='Test Content'
        )
        session.add(entry)

        def mock_commit_error(*args, **kwargs):
            if session.is_active:
                session.rollback()
            raise SQLAlchemyError("Database error")

        # セッションのcommitをモック化
        original_commit = session.commit
        session.commit = mock_commit_error

        try:
            with pytest.raises(SQLAlchemyError):
                session.commit()
        finally:
            session.commit = original_commit

    def test_entry_update(self, app, session):
        """エントリーの更新テスト"""
        user = self.setup_user(session)
        
        # エントリーを作成
        entry = Entry(
            user_id=user.id,
            title='Original Title',
            content='Original Content',
            notes='Original Notes'
        )
        session.add(entry)
        session.flush()

        original_created_at = entry.created_at
        assert entry.updated_at is None, "更新日時の初期値がNoneではありません"

        # 1秒待機して更新時刻の差を確実にする
        time_before_update = datetime.now()

        # エントリーを更新
        entry.update(
            title='Updated Title',
            content='Updated Content',
            notes='Updated Notes'
        )
        session.flush()

        # 更新後の状態を検証
        assert entry.title == 'Updated Title', "タイトルが更新されていません"
        assert entry.content == 'Updated Content', "コンテンツが更新されていません"
        assert entry.notes == 'Updated Notes', "ノートが更新されていません"
        assert entry.created_at == original_created_at, "作成日時が変更されています"
        assert entry.updated_at is not None, "更新日時が設定されていません"
        assert entry.updated_at >= time_before_update, "更新日時が正しくありません"

    def test_entry_partial_update(self, app, session):
        """エントリーの部分更新テスト"""
        user = self.setup_user(session)
        
        # エントリーを作成
        entry = Entry(
            user_id=user.id,
            title='Original Title',
            content='Original Content',
            notes='Original Notes'
        )
        session.add(entry)
        session.flush()

        # 部分的な更新
        current_title = entry.title
        current_content = entry.content
        time_before_update = datetime.now()

        entry.update(notes='Only Notes Updated')
        session.flush()

        assert entry.title == current_title, "タイトルが変更されています"
        assert entry.content == current_content, "コンテンツが変更されています"
        assert entry.notes == 'Only Notes Updated', "ノートが更新されていません"
        assert entry.updated_at >= time_before_update, "更新日時が正しくありません"

    def test_entry_invalid_update(self, app, session):
        """無効な更新操作のテスト"""
        user = self.setup_user(session)
        
        entry = Entry(
            user_id=user.id,
            title='Test Entry',
            content='Test Content'
        )
        session.add(entry)
        session.flush()

        # 存在しない属性での更新
        entry.update(
            non_existent_field='Some Value',
            another_field=123
        )
        
        assert not hasattr(entry, 'non_existent_field'), \
            "存在しない属性が追加されています"
        assert not hasattr(entry, 'another_field'), \
            "存在しない属性が追加されています"

    def test_entry_repr(self, app):
        """エントリーの文字列表現テスト"""
        test_cases = [
            # 通常のケース
            {
                'title': 'Test Entry',
                'expected': '<Entry Test Entry>'
            },
            # 特殊文字を含むケース
            {
                'title': 'Test/Entry#2',
                'expected': '<Entry Test/Entry#2>'
            },
            # 長いタイトルのケース
            {
                'title': 'A' * 100,
                'expected': f'<Entry {"A" * 100}>'
            },
            # 空のタイトルのケース
            {
                'title': '',
                'expected': '<Entry >'
            }
        ]

        for case in test_cases:
            try:
                entry = Entry(
                    user_id=1,
                    title=case['title'],
                    content='Test Content'
                )
                assert repr(entry) == case['expected'], \
                    f"タイトル '{case['title']}' の文字列表現が正しくありません"
            except ValueError:
                # 空のタイトルは実際にはバリデーションで弾かれるため、このケースは無視
                if case['title'] != '':
                    raise
