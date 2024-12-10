import pytest
from flask import Flask
from database import db, init_db, logger
import logging
from sqlalchemy import text
from models.user import User

class TestDatabase:
    def test_database_initialization(self, app):
        """データベース初期化のテスト"""
        # 新しいFlaskアプリケーションを作成
        test_app = Flask(__name__)
        test_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        with test_app.app_context():
            # データベースを初期化
            init_db(test_app)
            
            # データベース接続が確立されていることを確認
            assert db.engine is not None
            assert db.session is not None
            
            # テーブルが作成されていることを確認
            result = db.session.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            tables = [row[0] for row in result]
            assert 'users' in tables
            assert 'entries' in tables
            assert 'diary_items' in tables

    def test_database_logging(self, app, caplog):
        """データベースログ出力のテスト"""
        with caplog.at_level(logging.DEBUG):
            # 新しいFlaskアプリケーションを作成
            test_app = Flask(__name__)
            test_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
            
            with test_app.app_context():
                # データベースを初期化
                init_db(test_app)
                
                # ログメッセージを確認
                assert "Initializing database" in caplog.text
                assert "Creating all tables" in caplog.text
                assert "Database initialization complete" in caplog.text

    def test_database_uri_configuration(self, app):
        """データベースURI設定のテスト"""
        # 新しいFlaskアプリケーションを作成
        test_app = Flask(__name__)
        
        with test_app.app_context():
            # URIが設定されていない場合のデフォルト値をテスト
            init_db(test_app)
            assert test_app.config['SQLALCHEMY_DATABASE_URI'] == 'sqlite:///diary.db'
            assert test_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] is False
        
        # カスタムURIでの設定をテスト
        test_app2 = Flask(__name__)
        test_app2.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        with test_app2.app_context():
            init_db(test_app2)
            assert test_app2.config['SQLALCHEMY_DATABASE_URI'] == 'sqlite:///:memory:'

    def test_database_session_events(self, app, caplog):
        """データベースセッションイベントのテスト"""
        # 新しいFlaskアプリケーションを作成
        test_app = Flask(__name__)
        test_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        with test_app.app_context():
            init_db(test_app)
            
            with caplog.at_level(logging.DEBUG):
                caplog.clear()  # 既存のログをクリア
                
                # トランザクションを開始
                user = User(
                    userid='test_user',
                    name='Test User',
                    password='password',
                    is_admin=False,
                    is_locked=False,
                    is_visible=True,
                    login_attempts=0
                )
                db.session.add(user)
                db.session.commit()
                assert "Session committed" in caplog.text
                
                caplog.clear()  # ログをクリア
                
                # 無効な操作を試みてロールバックを発生させる
                try:
                    # 重複するユーザーIDを追加（一意性制約違反）
                    duplicate_user = User(
                        userid='test_user',  # 既存のユーザーIDを使用
                        name='Duplicate User',
                        password='password',
                        is_admin=False,
                        is_locked=False,
                        is_visible=True,
                        login_attempts=0
                    )
                    db.session.add(duplicate_user)
                    db.session.commit()
                except:
                    db.session.rollback()
                    assert "Session rollback" in caplog.text
                
                caplog.clear()  # ログをクリア
                
                # フラッシュイベントのテスト
                new_user = User(
                    userid='another_user',
                    name='Another User',
                    password='password',
                    is_admin=False,
                    is_locked=False,
                    is_visible=True,
                    login_attempts=0
                )
                db.session.add(new_user)
                db.session.flush()
                assert "Session flushed" in caplog.text

    def test_sql_query_logging(self, app, caplog):
        """SQLクエリログ出力のテスト"""
        # 新しいFlaskアプリケーションを作成
        test_app = Flask(__name__)
        test_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        with test_app.app_context():
            init_db(test_app)
            
            with caplog.at_level(logging.DEBUG):
                caplog.clear()  # 既存のログをクリア
                
                # テストクエリを実行
                db.session.execute(text("SELECT 1"))
                
                # SQLクエリがログに出力されていることを確認
                assert "SQL:" in caplog.text

    def test_database_error_handling(self, app):
        """データベースエラーハンドリングのテスト"""
        # 新しいFlaskアプリケーションを作成
        test_app = Flask(__name__)
        test_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        with test_app.app_context():
            init_db(test_app)
            
            # 無効なSQLを実行して例外が発生することを確認
            with pytest.raises(Exception):
                db.session.execute(text("INVALID SQL"))
