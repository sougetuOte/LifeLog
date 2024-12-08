from datetime import datetime
from sqlalchemy import Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from database import db
from models.base import Base

class Entry(db.Model, Base):
    __tablename__ = 'entries'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    notes: Mapped[str] = mapped_column(Text, nullable=False, default='')
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # リレーションシップ
    user: Mapped["User"] = relationship("User", back_populates="entries")
    items: Mapped[list["DiaryItem"]] = relationship("DiaryItem", back_populates="entry", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Entry {self.title}>"

    @validates('title')
    def validate_title(self, key, title):
        if len(title) > 100:
            raise ValueError('Title must be 100 characters or less')
        return title

    def update(self, **kwargs):
        """エントリーの属性を更新する"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now()
