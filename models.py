from datetime import datetime
from sqlalchemy import Boolean, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from database import db

class Base(DeclarativeBase):
    pass

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

# 初期データ作成用の関数
def create_initial_data():
    # 管理者ユーザーの作成
    admin = User(
        userid='admin',
        name='管理人',
        password='Admin3210',
        is_admin=True,
        created_at=datetime.now()
    )

    # テストユーザー1の作成
    tetsu = User(
        userid='tetsu',
        name='devilman',
        password='Tetsu3210',
        created_at=datetime.now()
    )

    # テストユーザー2の作成
    gento = User(
        userid='gento',
        name='gen chan',
        password='Gento3210',
        created_at=datetime.now()
    )

    db.session.add_all([admin, tetsu, gento])
    db.session.commit()

    # サンプル日記の作成
    admin_entry = Entry(
        user=admin,
        title='LifeLogの運営開始について',
        content='本日よりLifeLogの運営を開始しました。\n\n皆様に快適にご利用いただけるよう、以下のルールを設けさせていただきます：\n\n1. 他者への誹謗中傷は禁止\n2. 個人情報の投稿は控えめに\n3. 楽しく前向きな記録を心がけましょう\n\nご協力よろしくお願いいたします。',
        notes='天気：晴れ\n気分：わくわく',
        created_at=datetime.now()
    )

    tetsu_entry1 = Entry(
        user=tetsu,
        title='試合に向けて本格始動',
        content='今日から本格的なトレーニング期間に入る。\n\n朝一番でランニングから始めて、午後はジムでの練習。\n\n来月の試合までに必ず仕上げる！',
        notes='体重：75kg\n体調：絶好調\n気温：20℃',
        created_at=datetime.now()
    )

    # 活動項目の追加
    tetsu_items = [
        DiaryItem(
            entry=tetsu_entry1,
            item_name='筋トレ',
            item_content='スクワット 30回×3セット\nベンチプレス 80kg×10回×3セット\n腹筋 50回×3セット',
            created_at=datetime.now()
        ),
        DiaryItem(
            entry=tetsu_entry1,
            item_name='ランニング',
            item_content='朝：10km（50分）\n夜：5km（25分）',
            created_at=datetime.now()
        )
    ]

    db.session.add_all([admin_entry, tetsu_entry1] + tetsu_items)
    db.session.commit()
