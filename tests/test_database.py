import pytest
from flask import Flask
from database import db, init_db, logger, setup_event_listeners
import logging
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from models.user import User
from datetime import datetime

class TestDatabase:
    def test_database_initialization(self, app, session):
        """データベース初期化のテスト"""
        # データベース接続が確立されていることを確認
        assert db.engine is not None, "データベースエンジンが初期化されていません"
        assert db.session is not None, "データベースセッションが初期化されていません"
        
        # テーブルが作成されていることを確認
        result = session.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        tables = [row[0] for row in result]
        
        expected_tables = ['users', 'entries', 'diary_items']
        for table in expected_tables:
            assert table in tables, f"テーブル '{table}' が見つかりません"

    def test_database_logging(self, app, caplog):
        """データベースログ出力のテスト"""
        with caplog.at_level(logging.DEBUG):
            test_app = Flask(__name__)
            test_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
            
            with test_app.app_context():
                init_db(test_app)
                
                expected_logs = [
                    "Initializing database",
                    "Creating all tables",
                    "Database initialization complete"
                ]
                
                for log in expected_logs:
                    assert log in caplog.text, f"ログメッセージ '{log}' が出力されていません"

    def test_database_uri_configuration(self):
        """データベースURI設定のテスト"""
        # デフォルトURI設定のテスト
        test_app = Flask(__name__)
        with test_app.app_context():
            init_db(test_app)
            assert test_app.config['SQLALCHEMY_DATABASE_URI'] == 'sqlite:///diary.db', \
                "デフォルトのデータベースURIが正しくありません"
            assert test_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] is False, \
                "SQLALCHEMY_TRACK_MODIFICATIONSが正しく設定されていません"
        
        # カスタムURI設定のテスト
        test_app2 = Flask(__name__)
        test_app2.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        with test_app2.app_context():
            init_db(test_app2)
            assert test_app2.config['SQLALCHEMY_DATABASE_URI'] == 'sqlite:///:memory:', \
                "カスタムデータベースURIが正しく設定されていません"

    def test_database_commit_and_rollback(self, app, session, caplog):
        """コミットとロールバックのテスト"""
        # イベントリスナーを設定
        setup_event_listeners(app)

        with caplog.at_level(logging.DEBUG):
            caplog.clear()

            # 正常なトランザクションのテスト
            user = User(
                userid='test_user',
                name='Test User',
                password='password',
                is_admin=False,
                is_locked=False,
                is_visible=True,
                login_attempts=0,
                created_at=datetime.now()
            )
            session.add(user)
            session.commit()
            assert "Session committed" in caplog.text, "コミットイベントが記録されていません"
            
            caplog.clear()
            
            # ロールバックのテスト
            try:
                # 重複するユーザーIDを追加（一意性制約違反）
                duplicate_user = User(
                    userid='test_user',  # 既存のユーザーID
                    name='Duplicate User',
                    password='password',
                    is_admin=False,
                    is_locked=False,
                    is_visible=True,
                    login_attempts=0,
                    created_at=datetime.now()
                )
                session.add(duplicate_user)
                session.commit()
                pytest.fail("重複するユーザーIDが許可されました")
            except SQLAlchemyError:
                session.rollback()
                assert "Session rollback" in caplog.text, "ロールバックイベントが記録されていません"

    def test_database_flush(self, app, session, caplog):
        """フラッシュ操作のテスト"""
        # イベントリスナーを設定
        setup_event_listeners(app)

        with caplog.at_level(logging.DEBUG):
            caplog.clear()
            
            # フラッシュイベントのテスト
            user = User(
                userid='flush_test_user',
                name='Flush Test User',
                password='password',
                is_admin=False,
                is_locked=False,
                is_visible=True,
                login_attempts=0,
                created_at=datetime.now()
            )
            session.add(user)
            session.flush()
            assert "Session flushed" in caplog.text, "フラッシュイベントが記録されていません"

    def test_sql_query_logging(self, app, session, caplog):
        """SQLクエリログ出力のテスト"""
        # イベントリスナーを設定
        setup_event_listeners(app)

        with caplog.at_level(logging.DEBUG):
            caplog.clear()
            
            # テストクエリを実行
            session.execute(text("SELECT 1"))
            
            assert "SQL:" in caplog.text, "SQLクエリがログに記録されていません"

    def test_database_error_handling(self, app, session):
        """データベースエラーハンドリングのテスト"""
        # 無効なSQLを実行して例外が発生することを確認
        with pytest.raises(OperationalError) as exc_info:
            session.execute(text("INVALID SQL"))
        assert "syntax error" in str(exc_info.value).lower(), \
            "無効なSQLに対して適切なエラーが発生しませんでした"

        # トランザクションのロールバックを確認
        session.rollback()
        
        # セッションがまだ使用可能であることを確認
        result = session.execute(text("SELECT 1"))
        assert result.scalar() == 1, "エラー後のセッションが正常に機能していません"
