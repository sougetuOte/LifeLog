# tests/conftest.py
import os
import sys
import pytest
from datetime import datetime
from typing import Generator
from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# プロジェクトルートをPythonパスに追加
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# データベースモジュールをインポート
from database import db

@pytest.fixture(scope="session")
def app():
    """Flaskアプリケーションのフィクスチャ"""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['TESTING'] = True
    
    # SQLAlchemyの初期化
    db.init_app(app)
    
    # アプリケーションコンテキストをプッシュ
    ctx = app.app_context()
    ctx.push()
    
    # データベースの作成
    db.create_all()
    
    yield app
    
    # クリーンアップ
    db.session.remove()
    db.drop_all()
    ctx.pop()

@pytest.fixture(scope="function")
def session(app):
    """セッションのフィクスチャ"""
    connection = db.engine.connect()
    transaction = connection.begin()
    
    # セッションの作成
    session_factory = sessionmaker(bind=connection)
    session = scoped_session(session_factory)
    
    # グローバルセッションを一時的に置き換え
    old_session = db.session
    db.session = session
    
    yield session
    
    # クリーンアップ
    try:
        session.remove()
        # トランザクションがアクティブな場合のみロールバック
        if transaction.is_active:
            transaction.rollback()
    finally:
        connection.close()
        db.session = old_session

@pytest.fixture(scope="session")
def base_timestamp() -> datetime:
    return datetime(2024, 1, 1, 0, 0, 0)

@pytest.fixture(autouse=True)
def setup_teardown():
    # テスト前の準備
    print("Setting up test environment")
    yield
    # テスト後のクリーンアップ
    print("Cleaning up test environment")
