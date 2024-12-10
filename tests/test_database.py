import pytest
from flask import Flask
from database import db, init_db, setup_event_listeners
import logging
from unittest.mock import patch, MagicMock
from sqlalchemy import text
from models.user import User
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

class TestDatabase:
    def test_database_initialization(self):
        """データベース初期化のテスト"""
        # 新しいFlaskアプリケーションを作成
        test_app = Flask(__name__)
        
        # デフォルトのデータベースURI設定のテスト
        init_db(test_app)
        assert test_app.config['SQLALCHEMY_DATABASE_URI'] == 'sqlite:///diary.db'
        assert test_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] is False

        # カスタムURIでの初期化テスト
        test_app = Flask(__name__)
        test_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///custom.db'
        init_db(test_app)
        assert test_app.config['SQLALCHEMY_DATABASE_URI'] == 'sqlite:///custom.db'

    def test_database_logging(self, caplog):
        """データベースログ出力のテスト"""
        caplog.set_level(logging.DEBUG)
        
        # 新しいFlaskアプリケーションを作成
        test_app = Flask(__name__)
        
        # データベース初期化のログをテスト
        with caplog.at_level(logging.DEBUG):
            init_db(test_app)
            assert "Initializing database" in caplog.text
            assert "Database initialization complete" in caplog.text

    def test_database_uri_configuration(self):
        """データベースURI設定のテスト"""
        # URIが未設定の場合
        test_app = Flask(__name__)
        init_db(test_app)
        assert test_app.config['SQLALCHEMY_DATABASE_URI'] == 'sqlite:///diary.db'

        # URIが事前設定されている場合
        test_app = Flask(__name__)
        custom_uri = 'sqlite:///test.db'
        test_app.config['SQLALCHEMY_DATABASE_URI'] = custom_uri
        init_db(test_app)
        assert test_app.config['SQLALCHEMY_DATABASE_URI'] == custom_uri

    def test_event_listeners(self, caplog):
        """イベントリスナーのテスト"""
        caplog.set_level(logging.DEBUG)
        
        # 新しいFlaskアプリケーションを作成
        test_app = Flask(__name__)
        test_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        with test_app.app_context():
            init_db(test_app)
            setup_event_listeners(test_app)
            
            # ログをクリア
            caplog.clear()
            
            # SQLクエリのログ出力テスト
            db.session.execute(text('SELECT 1'))
            assert "SQL: SELECT 1" in caplog.text
            
            # フラッシュとコミットのテスト
            test_user = User(
                userid='test_user',
                name='Test User',
                password='password',
                is_admin=False,
                is_locked=False,
                is_visible=True,
                login_attempts=0
            )
            db.session.add(test_user)
            db.session.flush()
            assert "Session flushed" in caplog.text
            
            db.session.commit()
            assert "Session committed" in caplog.text
            
            # SQLAlchemyエラーとロールバックのテスト
            try:
                # 無効なSQLを実行してロールバックを強制
                db.session.execute(text('INVALID SQL'))
                pytest.fail("Should have raised an exception")
            except SQLAlchemyError:
                db.session.rollback()
                assert "Session rollback" in caplog.text

            # 整合性エラーとロールバックのテスト
            try:
                # 同じユーザーIDで再度追加を試みる
                duplicate_user = User(
                    userid='test_user',  # 既存のユーザーIDを使用
                    name='Another User',
                    password='password',
                    is_admin=False,
                    is_locked=False,
                    is_visible=True,
                    login_attempts=0
                )
                db.session.add(duplicate_user)
                db.session.commit()
                pytest.fail("Should have raised an IntegrityError")
            except IntegrityError:
                db.session.rollback()
                assert "Session rollback" in caplog.text

    def test_database_error_handling(self):
        """データベースエラーハンドリングのテスト"""
        test_app = Flask(__name__)
        test_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        init_db(test_app)
        
        with test_app.app_context():
            # SQLAlchemyエラーのテスト
            with pytest.raises(SQLAlchemyError):
                db.session.execute(text('INVALID SQL'))
                db.session.commit()

            # 整合性エラーのテスト
            db.create_all()
            test_user = User(
                userid='test_user',
                name='Test User',
                password='password',
                is_admin=False,
                is_locked=False,
                is_visible=True,
                login_attempts=0
            )
            db.session.add(test_user)
            db.session.commit()

            with pytest.raises(IntegrityError):
                duplicate_user = User(
                    userid='test_user',  # 既存のユーザーIDを使用
                    name='Another User',
                    password='password',
                    is_admin=False,
                    is_locked=False,
                    is_visible=True,
                    login_attempts=0
                )
                db.session.add(duplicate_user)
                db.session.commit()
