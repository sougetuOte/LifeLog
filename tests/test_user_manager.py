import pytest
from models.user_manager import UserManager
from models.user import User
from database import db
import uuid
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

@pytest.fixture(autouse=True)
def cleanup_database(app):
    """各テストの前にデータベースをクリーンアップ"""
    db.session.execute(text('DELETE FROM users'))
    db.session.commit()
    yield

@pytest.fixture
def user_manager():
    """UserManagerのフィクスチャ"""
    return UserManager()

@pytest.fixture
def test_users(app):
    """テストユーザーのフィクスチャ"""
    # 一意のユーザーIDを生成
    users = [
        User(
            userid=f"test_user_{uuid.uuid4().hex[:8]}",
            name=f"User {i}",
            password="password123",
            is_admin=False,
            is_visible=True if i < 3 else False,  # 3人は可視、2人は不可視
            is_locked=False
        ) for i in range(5)
    ]
    for user in users:
        db.session.add(user)
    db.session.commit()
    return users

def test_get_visible_users(user_manager, test_users):
    """可視状態のユーザー取得テスト"""
    visible_users = user_manager.get_visible_users()
    assert len(visible_users) == 3
    for user in visible_users:
        assert user.is_visible == True

def test_get_all_users(user_manager, test_users):
    """全ユーザー取得テスト"""
    all_users = user_manager.get_all_users()
    assert len(all_users) == 5

def test_toggle_admin_success(user_manager, test_users):
    """管理者権限切り替えテスト（成功）"""
    user = test_users[0]
    assert user.is_admin == False
    
    # 管理者権限を付与
    result = user_manager.toggle_admin(user.id, True)
    assert result == True
    assert user.is_admin == True
    
    # 管理者権限を削除
    result = user_manager.toggle_admin(user.id, False)
    assert result == True
    assert user.is_admin == False

def test_toggle_admin_failure(user_manager):
    """管理者権限切り替えテスト（失敗）"""
    result = user_manager.toggle_admin(999, True)  # 存在しないユーザーID
    assert result == False

def test_lock_user_success(user_manager, test_users):
    """ユーザーロックテスト（成功）"""
    user = test_users[0]
    assert user.is_locked == False
    
    result = user_manager.lock_user(user.id)
    assert result == True
    assert user.is_locked == True

def test_lock_user_failure(user_manager):
    """ユーザーロックテスト（失敗）"""
    result = user_manager.lock_user(999)  # 存在しないユーザーID
    assert result == False

def test_unlock_user_success(user_manager, test_users):
    """ユーザーロック解除テスト（成功）"""
    user = test_users[0]
    user.is_locked = True
    user.login_attempts = 3
    db.session.commit()
    
    result = user_manager.unlock_user(user.id)
    assert result == True
    assert user.is_locked == False
    assert user.login_attempts == 0

def test_unlock_user_failure(user_manager):
    """ユーザーロック解除テスト（失敗）"""
    result = user_manager.unlock_user(999)  # 存在しないユーザーID
    assert result == False

def test_error_handling(user_manager, app):
    """エラーハンドリングのテスト"""
    # SQLAlchemyErrorをシミュレート
    class MockSession:
        def execute(self, *args, **kwargs):
            raise SQLAlchemyError("Database error")
        
        def get(self, *args, **kwargs):
            raise SQLAlchemyError("Database error")
        
        def commit(self):
            raise SQLAlchemyError("Database error")
        
        def rollback(self):
            pass
    
    # 元のセッションを保存
    original_session = db.session
    
    try:
        # セッションをモックに置き換え
        db.session = MockSession()
        
        # 各メソッドでエラーが適切に処理されることを確認
        assert user_manager.get_visible_users() == []
        assert user_manager.get_all_users() == []
        assert user_manager.toggle_admin(1, True) == False
        assert user_manager.lock_user(1) == False
        assert user_manager.unlock_user(1) == False
    finally:
        # テスト後に元のセッションを復元
        db.session = original_session
