from datetime import datetime
from sqlalchemy import Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from database import db
from models.base import Base

class DiaryItem(db.Model, Base):
    __tablename__ = 'diary_items'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    entry_id: Mapped[int] = mapped_column(Integer, ForeignKey('entries.id'), nullable=False)
    item_name: Mapped[str] = mapped_column(String(100), nullable=False)
    item_content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now,
        server_default=db.func.current_timestamp()
    )

    # リレーションシップ
    entry: Mapped["Entry"] = relationship("Entry", back_populates="items")

    def __init__(self, **kwargs):
        # entryオブジェクトが渡された場合、entry_idを設定
        if 'entry' in kwargs and hasattr(kwargs['entry'], 'id'):
            kwargs['entry_id'] = kwargs['entry'].id

        # 必須フィールドの存在チェック
        if 'entry_id' not in kwargs:
            raise ValueError('Entry ID cannot be None')
        if 'item_name' not in kwargs:
            raise ValueError('Item name cannot be None')
        if 'item_content' not in kwargs:
            raise ValueError('Item content cannot be None')

        super().__init__(**kwargs)
        if 'created_at' not in kwargs:
            self.created_at = datetime.now()

    @validates('entry_id')
    def validate_entry_id(self, key, value):
        if value is None:
            raise ValueError('Entry ID cannot be None')
        if not isinstance(value, int):
            raise ValueError('Entry ID must be an integer')
        if value <= 0:
            raise ValueError('Entry ID must be a positive integer')
        return value

    @validates('item_name')
    def validate_item_name(self, key, value):
        if value is None:
            raise ValueError('Item name cannot be None')
        if not isinstance(value, str):
            raise ValueError('Item name must be a string')
        if len(value.strip()) == 0:
            raise ValueError('Item name cannot be empty')
        if len(value) > 100:
            raise ValueError('Item name must be 100 characters or less')
        return value

    @validates('item_content')
    def validate_item_content(self, key, value):
        if value is None:
            raise ValueError('Item content cannot be None')
        if not isinstance(value, str):
            raise ValueError('Item content must be a string')
        if len(value.strip()) == 0:
            raise ValueError('Item content cannot be empty')
        return value

    def __repr__(self):
        return f"<DiaryItem {self.item_name}>"
