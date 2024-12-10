from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import event
import logging

# ロガーの設定
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('database')

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

def setup_event_listeners(app):
    """イベントリスナーの設定"""
    with app.app_context():
        # SQLクエリのログ出力
        event.listen(
            db.engine,
            'before_cursor_execute',
            lambda conn, cursor, statement, parameters, context, executemany:
                logger.debug("SQL: %s\nParameters: %s", statement, parameters)
        )

        # セッションイベントのログ出力
        event.listen(
            db.session,
            'after_commit',
            lambda session: logger.debug("Session committed")
        )

        event.listen(
            db.session,
            'after_rollback',
            lambda session: logger.debug("Session rollback")
        )

        event.listen(
            db.session,
            'after_flush',
            lambda session, flush_context: logger.debug("Session flushed")
        )

def init_db(app):
    """データベースの初期化"""
    logger.debug("Initializing database")
    
    # データベースURIが設定されていない場合はデフォルト値を設定
    if not app.config.get('SQLALCHEMY_DATABASE_URI'):
        logger.debug("Setting database URI to sqlite:///diary.db")
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///diary.db'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # SQLAlchemyの初期化
    db.init_app(app)

    with app.app_context():
        # モデルのインポート
        from models.user import User
        from models.entry import Entry
        from models.diary_item import DiaryItem

        # イベントリスナーの設定
        setup_event_listeners(app)

        logger.debug("Creating all tables")
        db.create_all()
        logger.debug("Database initialization complete")
