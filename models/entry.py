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
    notes: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default='',
        server_default=''
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now,
        server_default=db.func.current_timestamp()
    )
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # リレーションシップ
    user: Mapped["User"] = relationship("User", back_populates="entries")
    items: Mapped[list["DiaryItem"]] = relationship("DiaryItem", back_populates="entry", cascade="all, delete-orphan")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if 'notes' not in kwargs:
            self.notes = ''
        if 'created_at' not in kwargs:
            self.created_at = datetime.now()

    def __repr__(self):
        return f"<Entry {self.title}>"

    @validates('title')
    def validate_title(self, key, title):
        if title is None:
            raise ValueError('Title cannot be None')
        if not isinstance(title, str):
            raise ValueError('Title must be a string')
        if len(title.strip()) == 0:
            raise ValueError('Title cannot be empty')
        if len(title) > 100:
            raise ValueError('Title must be 100 characters or less')
        return title

    @validates('content')
    def validate_content(self, key, content):
        if content is None:
            raise ValueError('Content cannot be None')
        if not isinstance(content, str):
            raise ValueError('Content must be a string')
        if len(content.strip()) == 0:
            raise ValueError('Content cannot be empty')
        return content

    @validates('notes')
    def validate_notes(self, key, notes):
        if notes is None:
            return ''
        if not isinstance(notes, str):
            raise ValueError('Notes must be a string')
        return notes

    @validates('user_id')
    def validate_user_id(self, key, user_id):
        if user_id is None:
            raise ValueError('User ID cannot be None')
        if not isinstance(user_id, int):
            raise ValueError('User ID must be an integer')
        if user_id <= 0:
            raise ValueError('User ID must be positive')
        return user_id

    def update(self, **kwargs):
        """エントリーの属性を更新する"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now()
