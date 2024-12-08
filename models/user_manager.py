from sqlalchemy import select
from database import db
from models.user import User

class UserManager:
    def get_visible_users(self):
        """可視状態のユーザーのみを取得"""
        stmt = select(User).filter_by(is_visible=True)
        return db.session.execute(stmt).scalars().all()

    def get_all_users(self):
        """全ユーザーを取得（管理者用）"""
        stmt = select(User)
        return db.session.execute(stmt).scalars().all()

    def toggle_admin(self, user_id: int, is_admin: bool) -> bool:
        """管理者権限の付与/削除"""
        user = db.session.get(User, user_id)
        if not user:
            return False
        
        user.is_admin = is_admin
        try:
            db.session.commit()
            return True
        except:
            db.session.rollback()
            return False

    def lock_user(self, user_id: int) -> bool:
        """ユーザーをロック"""
        user = db.session.get(User, user_id)
        if not user:
            return False
        
        user.is_locked = True
        try:
            db.session.commit()
            return True
        except:
            db.session.rollback()
            return False

    def unlock_user(self, user_id: int) -> bool:
        """ユーザーのロックを解除"""
        user = db.session.get(User, user_id)
        if not user:
            return False
        
        user.is_locked = False
        user.login_attempts = 0
        try:
            db.session.commit()
            return True
        except:
            db.session.rollback()
            return False
