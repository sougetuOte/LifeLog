# tests/test_user.py
import pytest
from datetime import datetime, timedelta
from models.user import User

class TestUser:
    def test_user_creation(self, session):
        user = User(
            userid="test_user",
            name="Test User",
            password="Test1234",  # 実際のパスワード要件に合わせて変更
            is_admin=False,
            is_locked=False,
            is_visible=True,
            login_attempts=0,
            created_at=datetime.now()
        )
        session.add(user)
        session.commit()

        saved_user = session.get(User, user.id)
        assert saved_user.userid == "test_user"
        assert saved_user.is_visible == True
        assert saved_user.login_attempts == 0

    def test_password_validation(self, session):
        user = User(
            userid="test_user",
            name="Test User",
            password="Test1234",
            created_at=datetime.now()
        )
        session.add(user)
        session.commit()

        assert user.check_password("Test1234") == True
        assert user.check_password("WrongPass") == False

    def test_lock_mechanism(self, session):
        user = User(
            userid="test_user",
            name="Test User",
            password="Test1234",
            login_attempts=0,
            created_at=datetime.now()
        )
        session.add(user)
        session.commit()
        
        # 3回失敗するまではロックされない
        for i in range(2):
            assert user.check_lock_status() == False
            user.login_attempts += 1
            session.commit()
        
        # 3回目で自動ロック
        user.login_attempts += 1
        session.commit()
        assert user.check_lock_status() == True
