import pytest
from flask import session
import json
import sys
import os

# プロジェクトルートをPythonパスに追加
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app import app as flask_app
from models import User, Entry, DiaryItem
from database import db

@pytest.fixture
def app():
    """Flaskアプリケーションのフィクスチャ"""
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    flask_app.config['TESTING'] = True
    flask_app.config['WTF_CSRF_ENABLED'] = False  # テスト時はCSRF保護を無効化
    
    # アプリケーションコンテキストをプッシュ
    ctx = flask_app.app_context()
    ctx.push()
    
    # データベースの作成
    db.create_all()
    
    yield flask_app
    
    # クリーンアップ
    db.session.remove()
    db.drop_all()
    ctx.pop()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def test_user(app):
    user = User(
        userid="testuser",
        name="Test User",
        password="password123",
        is_admin=False,
        is_visible=True
    )
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def admin_user(app):
    admin = User(
        userid="admin",
        name="Admin User",
        password="admin123",
        is_admin=True,
        is_visible=True
    )
    db.session.add(admin)
    db.session.commit()
    return admin

def test_index_route(client):
    """インデックスページのテスト"""
    response = client.get('/')
    assert response.status_code == 200

def test_login_route(client):
    """ログインページのテスト"""
    response = client.get('/login')
    assert response.status_code == 200

def test_login_success(client, test_user):
    """ログイン成功のテスト"""
    response = client.post('/api/login', 
        json={
            'userid': 'testuser',
            'password': 'password123'
        }
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['message'] == 'ログインしました'

def test_login_failure(client, test_user):
    """ログイン失敗のテスト"""
    response = client.post('/api/login', 
        json={
            'userid': 'testuser',
            'password': 'wrongpassword'
        }
    )
    assert response.status_code == 401
    data = json.loads(response.data)
    assert 'パスワードが正しくありません' in data['error']

def test_login_account_lock(client, test_user):
    """アカウントロックのテスト"""
    # 3回間違えてロック
    for _ in range(3):
        client.post('/api/login', 
            json={
                'userid': 'testuser',
                'password': 'wrongpassword'
            }
        )
    
    # 4回目の試行でロック確認
    response = client.post('/api/login', 
        json={
            'userid': 'testuser',
            'password': 'wrongpassword'
        }
    )
    assert response.status_code == 403
    data = json.loads(response.data)
    assert 'アカウントがロックされています' in data['error']

def test_logout(client, test_user):
    """ログアウトのテスト"""
    # まずログイン
    client.post('/api/login', 
        json={
            'userid': 'testuser',
            'password': 'password123'
        }
    )
    
    # ログアウト
    response = client.post('/api/logout')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['message'] == 'ログアウトしました'

def test_create_entry(client, test_user):
    """エントリー作成のテスト"""
    # ログイン
    client.post('/api/login', 
        json={
            'userid': 'testuser',
            'password': 'password123'
        }
    )
    
    # エントリー作成
    response = client.post('/entries', 
        json={
            'title': 'Test Entry',
            'content': 'Test Content',
            'notes': 'Test Notes',
            'items': [
                {
                    'item_name': 'Test Item',
                    'item_content': 'Test Item Content'
                }
            ]
        }
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['message'] == '投稿が完了しました'

def test_get_entries(client, test_user):
    """エントリー取得のテスト"""
    # エントリーを作成
    entry = Entry(
        user_id=test_user.id,
        title='Test Entry',
        content='Test Content',
        notes='Test Notes'
    )
    db.session.add(entry)
    db.session.commit()
    
    # エントリー一覧を取得
    response = client.get('/entries')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) > 0
    assert data[0]['title'] == 'Test Entry'

def test_update_entry(client, test_user):
    """エントリー更新のテスト"""
    # ログイン
    client.post('/api/login', 
        json={
            'userid': 'testuser',
            'password': 'password123'
        }
    )
    
    # エントリーを作成
    entry = Entry(
        user_id=test_user.id,
        title='Original Title',
        content='Original Content',
        notes='Original Notes'
    )
    db.session.add(entry)
    db.session.commit()
    
    # エントリーを更新
    response = client.put(f'/entries/{entry.id}', 
        json={
            'title': 'Updated Title',
            'content': 'Updated Content',
            'notes': 'Updated Notes',
            'items': []
        }
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['message'] == '更新が完了しました'

def test_delete_entry(client, test_user):
    """エントリー削除のテスト"""
    # ログイン
    client.post('/api/login', 
        json={
            'userid': 'testuser',
            'password': 'password123'
        }
    )
    
    # エントリーを作成
    entry = Entry(
        user_id=test_user.id,
        title='Test Entry',
        content='Test Content',
        notes='Test Notes'
    )
    db.session.add(entry)
    db.session.commit()
    
    # エントリーを削除
    response = client.delete(f'/entries/{entry.id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['message'] == '削除が完了しました'

def test_admin_get_users(client, admin_user):
    """管理者ユーザー一覧取得のテスト"""
    # 管理者でログイン
    client.post('/api/login', 
        json={
            'userid': 'admin',
            'password': 'admin123'
        }
    )
    
    # ユーザー一覧を取得
    response = client.get('/api/admin/users')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)

def test_admin_unlock_user(client, admin_user, test_user):
    """ユーザーアカウントのロック解除テスト"""
    # ユーザーをロック状態に
    test_user.is_locked = True
    db.session.commit()
    
    # 管理者でログイン
    client.post('/api/login', 
        json={
            'userid': 'admin',
            'password': 'admin123'
        }
    )
    
    # ユーザーのロックを解除
    response = client.post(f'/api/admin/users/{test_user.id}/unlock')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['message'] == 'アカウントのロックを解除しました'

def test_admin_toggle_admin(client, admin_user, test_user):
    """管理者権限の切り替えテスト"""
    # 管理者でログイン
    client.post('/api/login', 
        json={
            'userid': 'admin',
            'password': 'admin123'
        }
    )
    
    # 管理者権限を切り替え
    response = client.post(f'/api/admin/users/{test_user.id}/toggle-admin')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['message'] == '管理者権限を更新しました'

def test_admin_toggle_visibility(client, admin_user, test_user):
    """ユーザーの可視性切り替えテスト"""
    # 管理者でログイン
    client.post('/api/login', 
        json={
            'userid': 'admin',
            'password': 'admin123'
        }
    )
    
    # 可視性を切り替え
    response = client.post(f'/api/admin/users/{test_user.id}/toggle-visibility')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert '削除' in data['message'] or '復元' in data['message']
