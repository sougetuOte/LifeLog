from datetime import datetime
from sqlalchemy import Boolean, Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from database import db, logger
from models.base import Base

class User(db.Model, Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    userid: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(20), nullable=False)
    password: Mapped[str] = mapped_column(String(100), nullable=False)  # ハッシュ化されたパスワード
    is_admin: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_locked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_visible: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    login_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_login_attempt: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)

    # リレーションシップ
    entries: Mapped[list["Entry"]] = relationship("Entry", back_populates="user", cascade="all, delete-orphan")

    def __init__(self, **kwargs):
        # 必須フィールドの存在チェック
        if 'userid' not in kwargs:
            raise ValueError('User ID cannot be None')
        if 'name' not in kwargs:
            raise ValueError('Name cannot be None')
        if 'password' not in kwargs:
            raise ValueError('Password cannot be None')
        
        super().__init__(**kwargs)

    @validates('userid')
    def validate_userid(self, key, value):
        if not isinstance(value, str):
            raise ValueError('User ID must be a string')
        if len(value.strip()) == 0:
            raise ValueError('User ID cannot be empty')
        if len(value) > 20:
            raise ValueError('User ID must be 20 characters or less')
        return value

    @validates('name')
    def validate_name(self, key, value):
        if not isinstance(value, str):
            raise ValueError('Name must be a string')
        if len(value.strip()) == 0:
            raise ValueError('Name cannot be empty')
        if len(value) > 20:
            raise ValueError('Name must be 20 characters or less')
        return value

    @validates('password')
    def validate_password_field(self, key, value):
        if not isinstance(value, str):
            raise ValueError('Password must be a string')
        if len(value.strip()) == 0:
            raise ValueError('Password cannot be empty')
        return value

    def __repr__(self):
        return f"<User {self.userid}>"

    def check_password(self, password: str) -> bool:
        logger.debug(f"Checking password for user {self.userid}")
        logger.debug(f"Stored password: {self.password}")
        logger.debug(f"Input password: {password}")
        # TODO: パスワードのハッシュ化比較を実装
        result = self.password == password
        logger.debug(f"Password check result: {result}")
        return result

    def validate_password(self, password: str) -> bool:
        logger.debug(f"Validating password for user {self.userid}")
        # TODO: パスワードのバリデーションを実装
        # 現在はテスト用の簡易実装
        result = password == "correct_password"
        logger.debug(f"Password validation result: {result}")
        return result

    def check_lock_status(self) -> bool:
        logger.debug(f"Checking lock status for user {self.userid}")
        logger.debug(f"Current login attempts: {self.login_attempts}")
        logger.debug(f"Is locked: {self.is_locked}")
        # アカウントがロックされているか、ログイン試行回数が3回以上の場合はロック状態
        is_locked = self.is_locked or self.login_attempts >= 3
        logger.debug(f"Lock status check result: {is_locked}")
        return is_locked

    def increment_login_attempts(self):
        logger.debug(f"Incrementing login attempts for user {self.userid}")
        logger.debug(f"Current attempts: {self.login_attempts}")
        self.login_attempts += 1
        self.last_login_attempt = datetime.now()
        logger.debug(f"New attempts: {self.login_attempts}")
        if self.login_attempts >= 3:
            logger.debug("Account will be locked due to too many attempts")
            self.is_locked = True

    def reset_login_attempts(self):
        logger.debug(f"Resetting login attempts for user {self.userid}")
        self.login_attempts = 0
        self.last_login_attempt = None
        logger.debug("Login attempts reset complete")

    @classmethod
    def find_by_userid(cls, userid: str):
        logger.debug(f"Looking up user by userid: {userid}")
        user = cls.query.filter_by(userid=userid, is_visible=True).first()
        logger.debug(f"User lookup result: {user}")
        return user
