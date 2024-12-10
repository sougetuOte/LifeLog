import pytest
from datetime import datetime
from models.user import User
from models.user_manager import UserManager
from database import db
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select

class TestUserManager:
    def setup_user(self, session):
        """テスト用ユーザーをセットアップ"""
        user = User(
            userid='test_user',
            name='Test User',
            password='password',
            created_at=datetime.now()
        )
        session.add(user)
        session.flush()
        session.refresh(user)
        return user

    def test_get_visible_users(self, app, session):
        """可視ユーザー取得のテスト"""
        # 可視ユーザーを作成
        visible_user1 = User(
            userid='visible1',
            name='Visible User 1',
            password='password',
            is_visible=True,
            created_at=datetime.now()
        )
        visible_user2 = User(
            userid='visible2',
            name='Visible User 2',
            password='password',
            is_visible=True,
            created_at=datetime.now()
        )
        
        # 非可視ユーザーを作成
        invisible_user = User(
            userid='invisible',
            name='Invisible User',
            password='password',
            is_visible=False,
            created_at=datetime.now()
        )
        
        session.add_all([visible_user1, visible_user2, invisible_user])
        session.flush()

        manager = UserManager()
        visible_users = manager.get_visible_users()

        # 可視ユーザーのみが取得されることを確認
        assert len(visible_users) == 2
        assert visible_user1 in visible_users
        assert visible_user2 in visible_users
        assert invisible_user not in visible_users

        # useridでソートされていることを確認
        assert visible_users == sorted(visible_users, key=lambda u: u.userid)

    def test_get_all_users(self, app, session):
        """全ユーザー取得のテスト"""
        # 様々な状態のユーザーを作成
        users = [
            User(userid='admin', name='Admin User', password='password',
                is_admin=True, is_visible=True, created_at=datetime.now()),
            User(userid='locked', name='Locked User', password='password',
                is_locked=True, is_visible=True, created_at=datetime.now()),
            User(userid='invisible', name='Invisible User', password='password',
                is_visible=False, created_at=datetime.now()),
            User(userid='normal', name='Normal User', password='password',
                is_visible=True, created_at=datetime.now())
        ]
        
        session.add_all(users)
        session.flush()

        manager = UserManager()
        all_users = manager.get_all_users()

        # すべてのユーザーが取得されることを確認
        assert len(all_users) == 4
        for user in users:
            assert user in all_users

        # useridでソートされていることを確認
        assert all_users == sorted(all_users, key=lambda u: u.userid)

    def test_get_users_database_error(self, app, session, caplog):
        """ユーザー取得時のデータベースエラー処理をテスト"""
        manager = UserManager()

        def mock_session_error(*args, **kwargs):
            raise SQLAlchemyError("Database error")

        # get_visible_usersのエラー処理
        original_execute = db.session.execute
        db.session.execute = mock_session_error
        try:
            users = manager.get_visible_users()
            assert len(users) == 0
            assert "Error getting visible users: Database error" in caplog.text
        finally:
            db.session.execute = original_execute

        caplog.clear()

        # get_all_usersのエラー処理
        db.session.execute = mock_session_error
        try:
            users = manager.get_all_users()
            assert len(users) == 0
            assert "Error getting all users: Database error" in caplog.text
        finally:
            db.session.execute = original_execute

    def test_toggle_admin_error(self, app, session, caplog):
        """toggle_admin メソッドのエラーハンドリングをテスト"""
        manager = UserManager()
        user = self.setup_user(session)
        user_id = user.id

        def mock_commit_error(*args, **kwargs):
            session.rollback()  # 即座にロールバック
            raise SQLAlchemyError("Database error")

        # db.sessionのcommitをモック化
        original_commit = db.session.commit
        db.session.commit = mock_commit_error

        try:
            result = manager.toggle_admin(user_id, True)
            assert result is False
            assert "Error toggling admin status for user" in caplog.text
        finally:
            db.session.commit = original_commit

        # 状態を確認
        session.expire(user)
        session.refresh(user)
        assert not user.is_admin

    def test_lock_user_error(self, app, session, caplog):
        """lock_user メソッドのエラーハンドリングをテスト"""
        manager = UserManager()
        user = self.setup_user(session)
        user_id = user.id

        def mock_commit_error(*args, **kwargs):
            session.rollback()  # 即座にロールバック
            raise SQLAlchemyError("Database error")

        # db.sessionのcommitをモック化
        original_commit = db.session.commit
        db.session.commit = mock_commit_error

        try:
            result = manager.lock_user(user_id)
            assert result is False
            assert "Error locking user" in caplog.text
        finally:
            db.session.commit = original_commit

        # 状態を確認
        session.expire(user)
        session.refresh(user)
        assert not user.is_locked

    def test_unlock_user_error(self, app, session, caplog):
        """unlock_user メソッドのエラーハンドリングをテスト"""
        manager = UserManager()
        user = self.setup_user(session)

        # ユーザーをロック状態に設定
        user.is_locked = True
        user.login_attempts = 3
        session.flush()
        session.refresh(user)

        def mock_commit_error(*args, **kwargs):
            session.rollback()  # 即座にロールバック
            raise SQLAlchemyError("Database error")

        # db.sessionのcommitをモック化
        original_commit = db.session.commit
        db.session.commit = mock_commit_error

        try:
            result = manager.unlock_user(user.id)
            assert result is False
            assert "Error unlocking user" in caplog.text
        finally:
            db.session.commit = original_commit

        # 状態を確認
        session.expire(user)
        session.refresh(user)
        assert user.is_locked
        assert user.login_attempts == 3

    def test_database_error_handling_user_not_found(self, app, session, caplog):
        """存在しないユーザーに対するエラー処理のテスト"""
        manager = UserManager()
        non_existent_id = 9999

        # toggle_adminのエラー処理
        assert manager.toggle_admin(non_existent_id, True) is False
        assert f"User not found: {non_existent_id}" in caplog.text

        caplog.clear()

        # lock_userのエラー処理
        assert manager.lock_user(non_existent_id) is False
        assert f"User not found: {non_existent_id}" in caplog.text

        caplog.clear()

        # unlock_userのエラー処理
        assert manager.unlock_user(non_existent_id) is False
        assert f"User not found: {non_existent_id}" in caplog.text

    def test_concurrent_operations(self, app, session):
        """同時操作のテスト"""
        # テストユーザーを作成
        user = self.setup_user(session)

        manager1 = UserManager()
        manager2 = UserManager()

        # 同時にロック操作を実行
        assert manager1.lock_user(user.id) is True
        assert manager2.lock_user(user.id) is True
        session.refresh(user)
        assert user.is_locked is True

        # 同時にアンロック操作を実行
        assert manager1.unlock_user(user.id) is True
        assert manager2.unlock_user(user.id) is True
        session.refresh(user)
        assert user.is_locked is False

        # 同時に管理者権限を変更
        assert manager1.toggle_admin(user.id, True) is True
        assert manager2.toggle_admin(user.id, False) is True
        session.refresh(user)
        assert user.is_admin is False
