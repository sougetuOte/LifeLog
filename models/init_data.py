from datetime import datetime
from database import db
from models.user import User
from models.entry import Entry
from models.diary_item import DiaryItem

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
