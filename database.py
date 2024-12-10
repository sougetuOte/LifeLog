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

# SQLクエリのログ出力
@event.listens_for(db.engine, 'before_cursor_execute')
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    logger.debug("SQL: %s", statement)
    logger.debug("Parameters: %s", parameters)

# セッション管理
def init_db(app):
    logger.debug("Initializing database")
    if not app.config.get('SQLALCHEMY_DATABASE_URI'):
        logger.debug("Setting database URI to sqlite:///diary.db")
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///diary.db'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.init_app(app)

    with app.app_context():
        logger.debug("Creating all tables")
        db.create_all()
        logger.debug("Database initialization complete")

# セッションイベントのログ出力
@event.listens_for(db.session, 'after_commit')
def after_commit(session):
    logger.debug("Session committed")

@event.listens_for(db.session, 'after_rollback')
def after_rollback(session):
    logger.debug("Session rollback")

@event.listens_for(db.session, 'after_flush')
def after_flush(session, flush_context):
    logger.debug("Session flushed")
    for obj in session.new:
        logger.debug("New object: %s", obj)
    for obj in session.dirty:
        logger.debug("Modified object: %s", obj)
    for obj in session.deleted:
        logger.debug("Deleted object: %s", obj)
