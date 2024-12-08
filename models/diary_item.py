from datetime import datetime
from sqlalchemy import Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import db
from models.base import Base

class DiaryItem(db.Model, Base):
    __tablename__ = 'diary_items'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    entry_id: Mapped[int] = mapped_column(Integer, ForeignKey('entries.id'), nullable=False)
    item_name: Mapped[str] = mapped_column(String(100), nullable=False)
    item_content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)

    # リレーションシップ
    entry: Mapped["Entry"] = relationship("Entry", back_populates="items")

    def __repr__(self):
        return f"<DiaryItem {self.item_name}>"
