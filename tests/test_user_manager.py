# tests/test_user_manager.py
import pytest
from datetime import datetime
from models.user_manager import UserManager
from models.user import User

class TestUserManager:
    def test_user_visibility_control(self, session):
        # テストユーザーを作成
        visible_user = User(
            userid="visible_user",
            name="Visible User",
            password="Test1234",
            is_visible=True,
            created_at=datetime.now()
        )
        invisible_user = User(
            userid="invisible_user",
            name="Invisible User",
            password="Test1234",
            is_visible=False,
            created_at=datetime.now()
        )
        session.add_all([visible_user, invisible_user])
        session.commit()

        manager = UserManager()
        
        # 可視ユーザーのみを取得
        visible_users = manager.get_visible_users()
        assert len(visible_users) == 1
        assert all(user.is_visible for user in visible_users)
        
        # 全ユーザーを取得（管理者用）
        all_users = manager.get_all_users()
        assert len(all_users) == 2

    def test_admin_operations(self, session):
        # テストユーザーを作成
        user = User(
            userid="test_user",
            name="Test User",
            password="Test1234",
            is_admin=False,
            created_at=datetime.now()
        )
        session.add(user)
        session.commit()

        manager = UserManager()
        
        # 管理者権限の付与
        assert manager.toggle_admin(user.id, True) == True
        session.refresh(user)
        assert user.is_admin == True

        # 管理者権限の削除
        assert manager.toggle_admin(user.id, False) == True
        session.refresh(user)
        assert user.is_admin == False

    def test_lock_operations(self, session):
        # テストユーザーを作成
        user = User(
            userid="test_user",
            name="Test User",
            password="Test1234",
            is_locked=False,
            created_at=datetime.now()
        )
        session.add(user)
        session.commit()

        manager = UserManager()

        # ユーザーをロック
        assert manager.lock_user(user.id) == True
        session.refresh(user)
        assert user.is_locked == True

        # ユーザーのロックを解除
        assert manager.unlock_user(user.id) == True
        session.refresh(user)
        assert user.is_locked == False
        assert user.login_attempts == 0
