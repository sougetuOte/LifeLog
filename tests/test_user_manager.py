import pytest
from datetime import datetime
from models.user_manager import UserManager
from models.user import User
from database import db
from sqlalchemy import select, text
from unittest.mock import patch
from sqlalchemy.exc import SQLAlchemyError

class TestUserManager:
    def setup_method(self, method):
        """各テストメソッドの前にデータベースをクリア"""
        with db.session() as session:
            session.execute(text('DELETE FROM diary_items'))
            session.execute(text('DELETE FROM entries'))
            session.execute(text('DELETE FROM users'))
            session.commit()

    def create_test_users(self, app):
        """テスト用のユーザーを作成"""
        with app.app_context():
            users = [
                User(
                    userid='admin',
                    name='管理者',
                    password='password',
                    is_admin=True,
                    is_locked=False,
                    is_visible=True,
                    login_attempts=0,
                    created_at=datetime.now()
                ),
                User(
                    userid='user1',
                    name='一般ユーザー1',
                    password='password',
                    is_admin=False,
                    is_locked=False,
                    is_visible=True,
                    login_attempts=0,
                    created_at=datetime.now()
                ),
                User(
                    userid='user2',
                    name='一般ユーザー2',
                    password='password',
                    is_admin=False,
                    is_locked=False,
                    is_visible=False,  # 非表示ユーザー
                    login_attempts=0,
                    created_at=datetime.now()
                )
            ]
            db.session.add_all(users)
            db.session.commit()
            return users

    def test_get_visible_users(self, app):
        """可視状態のユーザー取得テスト"""
        users = self.create_test_users(app)
        
        with app.app_context():
            manager = UserManager()
            visible_users = manager.get_visible_users()
            
            # 可視状態のユーザーのみが取得されることを確認
            assert len(visible_users) == 2
            assert all(user.is_visible for user in visible_users)
            
            # ユーザーIDでソートされていることを確認
            assert visible_users[0].userid == 'admin'
            assert visible_users[1].userid == 'user1'

    def test_get_all_users(self, app):
        """全ユーザー取得テスト"""
        users = self.create_test_users(app)
        
        with app.app_context():
            manager = UserManager()
            all_users = manager.get_all_users()
            
            # 全てのユーザーが取得されることを確認
            assert len(all_users) == 3
            
            # ユーザーIDでソートされていることを確認
            assert all_users[0].userid == 'admin'
            assert all_users[1].userid == 'user1'
            assert all_users[2].userid == 'user2'

    def test_toggle_admin(self, app):
        """管理者権限の切り替えテスト"""
        users = self.create_test_users(app)
        
        with app.app_context():
            manager = UserManager()
            user = db.session.execute(select(User).filter_by(userid='user1')).scalar_one()
            
            # 管理者権限を付与
            assert manager.toggle_admin(user.id, True) is True
            db.session.refresh(user)
            assert user.is_admin is True
            
            # 管理者権限を削除
            assert manager.toggle_admin(user.id, False) is True
            db.session.refresh(user)
            assert user.is_admin is False
            
            # 存在しないユーザーIDの場合
            assert manager.toggle_admin(9999, True) is False

    def test_lock_user(self, app):
        """ユーザーのロックテスト"""
        users = self.create_test_users(app)
        
        with app.app_context():
            manager = UserManager()
            user = db.session.execute(select(User).filter_by(userid='user1')).scalar_one()
            
            # ユーザーをロック
            assert manager.lock_user(user.id) is True
            db.session.refresh(user)
            assert user.is_locked is True
            
            # 存在しないユーザーIDの場合
            assert manager.lock_user(9999) is False

    def test_unlock_user(self, app):
        """ユーザーのロック解除テスト"""
        users = self.create_test_users(app)
        
        with app.app_context():
            manager = UserManager()
            user = db.session.execute(select(User).filter_by(userid='user1')).scalar_one()
            
            # 事前にユーザーをロック
            user.is_locked = True
            user.login_attempts = 3
            db.session.commit()
            
            # ロック解除
            assert manager.unlock_user(user.id) is True
            db.session.refresh(user)
            assert user.is_locked is False
            assert user.login_attempts == 0
            
            # 存在しないユーザーIDの場合
            assert manager.unlock_user(9999) is False

    def test_database_error_handling(self, app):
        """データベースエラーハンドリングのテスト"""
        with app.app_context():
            manager = UserManager()
            
            # SQLAlchemyErrorを発生させるようにモック化
            with patch('sqlalchemy.orm.session.Session.execute') as mock_execute:
                mock_execute.side_effect = SQLAlchemyError("Test database error")
                
                # 各メソッドがエラーを適切に処理することを確認
                assert manager.get_visible_users() == []
                assert manager.get_all_users() == []
            
            with patch('sqlalchemy.orm.session.Session.get') as mock_get:
                mock_get.side_effect = SQLAlchemyError("Test database error")
                
                assert manager.toggle_admin(1, True) is False
                assert manager.lock_user(1) is False
                assert manager.unlock_user(1) is False
