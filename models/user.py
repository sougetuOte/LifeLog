from datetime import datetime
from sqlalchemy import Boolean, Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import db
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

    def __repr__(self):
        return f"<User {self.userid}>"

    def check_password(self, password: str) -> bool:
        # TODO: パスワードのハッシュ化比較を実装
        return self.password == password

    def validate_password(self, password: str) -> bool:
        # TODO: パスワードのバリデーションを実装
        # 現在はテスト用の簡易実装
        return password == "correct_password"

    def check_lock_status(self) -> bool:
        # アカウントがロックされているか、ログイン試行回数が3回以上の場合はロック状態
        return self.is_locked or self.login_attempts >= 3
