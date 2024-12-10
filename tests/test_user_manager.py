import pytest
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from models.user import User
from models.user_manager import UserManager
from database import db

class TestUserManager:
    def setup_method(self):
        """各テストメソッドの前にデータベースをクリアし、テストユーザーを作成"""
        self.user_manager = UserManager()
        
        # データベースをクリア
        with db.session() as session:
            session.query(User).delete()
            session.commit()
        
        # テストユーザーを作成
        self.user1 = User(
            userid='test1',
            name='Test User 1',
            password='Password1',
            is_visible=True,
            created_at=datetime.now()
        )
        self.user2 = User(
            userid='test2',
            name='Test User 2',
            password='Password2',
            is_visible=False,
            created_at=datetime.now()
        )
        self.user3 = User(
            userid='test3',
            name='Test User 3',
            password='Password3',
            is_visible=True,
            created_at=datetime.now()
        )
        
        with db.session() as session:
            session.add(self.user1)
            session.add(self.user2)
            session.add(self.user3)
            session.commit()
            # IDを保存
            self.user1_id = self.user1.id
            self.user2_id = self.user2.id
            self.user3_id = self.user3.id

    def teardown_method(self):
        """各テストメソッドの後にデータベースをクリア"""
        with db.session() as session:
            session.query(User).delete()
            session.commit()

    def test_get_visible_users(self, app):
        """可視状態のユーザー取得テスト"""
        with app.app_context():
            users = self.user_manager.get_visible_users()
            assert len(users) == 2
            assert all(user.is_visible for user in users)
            user_ids = [user.userid for user in users]
            assert 'test1' in user_ids
            assert 'test3' in user_ids
            assert 'test2' not in user_ids

    def test_get_visible_users_error(self, app, mocker):
        """可視状態のユーザー取得時のエラーハンドリングテスト"""
        with app.app_context():
            # SQLAlchemyErrorを発生させる
            mocker.patch('sqlalchemy.orm.Session.execute', side_effect=SQLAlchemyError("Test error"))
            users = self.user_manager.get_visible_users()
            assert users == []

    def test_get_all_users(self, app):
        """全ユーザー取得テスト"""
        with app.app_context():
            users = self.user_manager.get_all_users()
            assert len(users) == 3
            assert all(user.userid in ['test1', 'test2', 'test3'] for user in users)

    def test_get_all_users_error(self, app, mocker):
        """全ユーザー取得時のエラーハンドリングテスト"""
        with app.app_context():
            # SQLAlchemyErrorを発生させる
            mocker.patch('sqlalchemy.orm.Session.execute', side_effect=SQLAlchemyError("Test error"))
            users = self.user_manager.get_all_users()
            assert users == []

    def test_toggle_admin_grant(self, app):
        """管理者権限付与テスト"""
        with app.app_context():
            with db.session() as session:
                user = session.get(User, self.user1_id)
                assert not user.is_admin
                
                result = self.user_manager.toggle_admin(self.user1_id, True)
                assert result
                
                session.refresh(user)
                assert user.is_admin

    def test_toggle_admin_revoke(self, app):
        """管理者権限削除テスト"""
        with app.app_context():
            with db.session() as session:
                user = session.get(User, self.user1_id)
                user.is_admin = True
                session.commit()
                
                result = self.user_manager.toggle_admin(self.user1_id, False)
                assert result
                
                session.refresh(user)
                assert not user.is_admin

    def test_toggle_admin_nonexistent_user(self, app):
        """存在しないユーザーの管理者権限変更テスト"""
        with app.app_context():
            result = self.user_manager.toggle_admin(9999, True)
            assert not result

    def test_toggle_admin_error(self, app, mocker):
        """管理者権限変更時のエラーハンドリングテスト"""
        with app.app_context():
            # SQLAlchemyErrorを発生させる
            mocker.patch('sqlalchemy.orm.Session.commit', side_effect=SQLAlchemyError("Test error"))
            result = self.user_manager.toggle_admin(self.user1_id, True)
            assert not result
            
            with db.session() as session:
                user = session.get(User, self.user1_id)
                assert not user.is_admin

    def test_lock_user(self, app):
        """ユーザーロックテスト"""
        with app.app_context():
            with db.session() as session:
                user = session.get(User, self.user1_id)
                assert not user.is_locked
                
                result = self.user_manager.lock_user(self.user1_id)
                assert result
                
                session.refresh(user)
                assert user.is_locked

    def test_lock_nonexistent_user(self, app):
        """存在しないユーザーのロックテスト"""
        with app.app_context():
            result = self.user_manager.lock_user(9999)
            assert not result

    def test_lock_user_error(self, app, mocker):
        """ユーザーロック時のエラーハンドリングテスト"""
        with app.app_context():
            # SQLAlchemyErrorを発生させる
            mocker.patch('sqlalchemy.orm.Session.commit', side_effect=SQLAlchemyError("Test error"))
            result = self.user_manager.lock_user(self.user1_id)
            assert not result
            
            with db.session() as session:
                user = session.get(User, self.user1_id)
                assert not user.is_locked

    def test_unlock_user(self, app):
        """ユーザーロック解除テスト"""
        with app.app_context():
            with db.session() as session:
                user = session.get(User, self.user1_id)
                user.is_locked = True
                user.login_attempts = 3
                session.commit()
                
                result = self.user_manager.unlock_user(self.user1_id)
                assert result
                
                session.refresh(user)
                assert not user.is_locked
                assert user.login_attempts == 0

    def test_unlock_nonexistent_user(self, app):
        """存在しないユーザーのロック解除テスト"""
        with app.app_context():
            result = self.user_manager.unlock_user(9999)
            assert not result

    def test_unlock_user_error(self, app, mocker):
        """ユーザーロック解除時のエラーハンドリングテスト"""
        with app.app_context():
            with db.session() as session:
                user = session.get(User, self.user1_id)
                user.is_locked = True
                user.login_attempts = 3
                session.commit()
            
            # SQLAlchemyErrorを発生させる
            mocker.patch('sqlalchemy.orm.Session.commit', side_effect=SQLAlchemyError("Test error"))
            result = self.user_manager.unlock_user(self.user1_id)
            assert not result
            
            with db.session() as session:
                user = session.get(User, self.user1_id)
                assert user.is_locked
                assert user.login_attempts == 3
