from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from database import db, logger
from models.user import User

class UserManager:
    def get_visible_users(self):
        """可視状態のユーザーのみを取得"""
        try:
            stmt = select(User).filter_by(is_visible=True).order_by(User.userid)
            return db.session.execute(stmt).scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting visible users: {e}")
            return []

    def get_all_users(self):
        """全ユーザーを取得（管理者用）"""
        try:
            stmt = select(User).order_by(User.userid)
            return db.session.execute(stmt).scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting all users: {e}")
            return []

    def toggle_admin(self, user_id: int, is_admin: bool) -> bool:
        """管理者権限の付与/削除"""
        try:
            user = db.session.get(User, user_id)
            if not user:
                logger.warning(f"User not found: {user_id}")
                return False
            
            user.is_admin = is_admin
            db.session.commit()
            logger.info(f"Admin status updated for user {user_id}: {is_admin}")
            return True
        except SQLAlchemyError as e:
            logger.error(f"Error toggling admin status for user {user_id}: {e}")
            db.session.rollback()
            return False

    def lock_user(self, user_id: int) -> bool:
        """ユーザーをロック"""
        try:
            user = db.session.get(User, user_id)
            if not user:
                logger.warning(f"User not found: {user_id}")
                return False
            
            user.is_locked = True
            db.session.commit()
            logger.info(f"User locked: {user_id}")
            return True
        except SQLAlchemyError as e:
            logger.error(f"Error locking user {user_id}: {e}")
            db.session.rollback()
            return False

    def unlock_user(self, user_id: int) -> bool:
        """ユーザーのロックを解除"""
        try:
            user = db.session.get(User, user_id)
            if not user:
                logger.warning(f"User not found: {user_id}")
                return False
            
            user.is_locked = False
            user.login_attempts = 0
            db.session.commit()
            logger.info(f"User unlocked: {user_id}")
            return True
        except SQLAlchemyError as e:
            logger.error(f"Error unlocking user {user_id}: {e}")
            db.session.rollback()
            return False
