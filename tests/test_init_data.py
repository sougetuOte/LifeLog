import pytest
from datetime import datetime
from models.init_data import create_initial_data
from models.user import User
from models.entry import Entry
from models.diary_item import DiaryItem
from database import db
from sqlalchemy import select, text

class TestInitData:
    def setup_method(self, method):
        """各テストメソッドの前にデータベースをクリア"""
        with db.session() as session:
            session.execute(text('DELETE FROM diary_items'))
            session.execute(text('DELETE FROM entries'))
            session.execute(text('DELETE FROM users'))
            session.commit()

    def test_create_initial_data(self, app):
        """初期データ作成の基本テスト"""
        with app.app_context():
            # 初期データを作成
            create_initial_data()

            with db.session() as session:
                # ユーザーの確認
                admin = session.execute(select(User).filter_by(userid='admin')).scalar_one()
                assert admin.name == '管理人'
                assert admin.is_admin is True
                assert admin.password == 'Admin3210'

                tetsu = session.execute(select(User).filter_by(userid='tetsu')).scalar_one()
                assert tetsu.name == 'devilman'
                assert tetsu.is_admin is False
                assert tetsu.password == 'Tetsu3210'

                gento = session.execute(select(User).filter_by(userid='gento')).scalar_one()
                assert gento.name == 'gen chan'
                assert gento.is_admin is False
                assert gento.password == 'Gento3210'

                # 投稿の確認
                admin_entry = session.execute(
                    select(Entry).filter_by(user_id=admin.id, title='LifeLogの運営開始について')
                ).scalar_one()
                assert '本日よりLifeLogの運営を開始しました' in admin_entry.content
                assert '天気：晴れ' in admin_entry.notes
                assert admin_entry.user == admin

                tetsu_entry = session.execute(
                    select(Entry).filter_by(user_id=tetsu.id, title='試合に向けて本格始動')
                ).scalar_one()
                assert '本格的なトレーニング期間' in tetsu_entry.content
                assert '体重：75kg' in tetsu_entry.notes
                assert tetsu_entry.user == tetsu

                # DiaryItemの確認
                diary_items = session.execute(
                    select(DiaryItem).filter_by(entry_id=tetsu_entry.id)
                ).scalars().all()
                assert len(diary_items) == 2
                
                training_item = next(item for item in diary_items if item.item_name == '筋トレ')
                assert 'スクワット' in training_item.item_content
                assert 'ベンチプレス' in training_item.item_content
                assert training_item.entry == tetsu_entry

                running_item = next(item for item in diary_items if item.item_name == 'ランニング')
                assert '朝：10km' in running_item.item_content
                assert '夜：5km' in running_item.item_content
                assert running_item.entry == tetsu_entry

    def test_create_initial_data_idempotency(self, app):
        """初期データ作成の冪等性テスト"""
        with app.app_context():
            # 2回実行しても問題ないことを確認
            create_initial_data()
            
            with db.session() as session:
                # ユーザー数を記録
                user_count_1 = len(session.execute(select(User)).scalars().all())
                entry_count_1 = len(session.execute(select(Entry)).scalars().all())
                item_count_1 = len(session.execute(select(DiaryItem)).scalars().all())

            create_initial_data()

            with db.session() as session:
                # 2回目実行後も同じ数であることを確認
                user_count_2 = len(session.execute(select(User)).scalars().all())
                entry_count_2 = len(session.execute(select(Entry)).scalars().all())
                item_count_2 = len(session.execute(select(DiaryItem)).scalars().all())

            assert user_count_1 == user_count_2
            assert entry_count_1 == entry_count_2
            assert item_count_1 == item_count_2

    def test_create_initial_data_with_existing_users(self, app):
        """既存ユーザーがいる場合のテスト"""
        with app.app_context():
            # 先に管理者ユーザーを作成
            with db.session() as session:
                admin = User(
                    userid='admin',
                    name='既存管理者',
                    password='ExistingAdmin123',
                    is_admin=True,
                    created_at=datetime.now()
                )
                session.add(admin)
                session.commit()

            # 初期データを作成
            create_initial_data()

            with db.session() as session:
                # 既存の管理者が上書きされていないことを確認
                admin = session.execute(select(User).filter_by(userid='admin')).scalar_one()
                assert admin.name == '既存管理者'
                assert admin.password == 'ExistingAdmin123'

    def test_create_initial_data_with_existing_entries(self, app):
        """既存のエントリーがある場合のテスト"""
        with app.app_context():
            # 先にユーザーとエントリーを作成
            with db.session() as session:
                admin = User(
                    userid='admin',
                    name='管理人',
                    password='Admin3210',
                    is_admin=True,
                    created_at=datetime.now()
                )
                session.add(admin)
                session.commit()

                admin_id = admin.id

                existing_entry = Entry(
                    user=admin,
                    title='LifeLogの運営開始について',
                    content='既存の内容です',
                    notes='既存のノート',
                    created_at=datetime.now()
                )
                session.add(existing_entry)
                session.commit()

            # 初期データを作成
            create_initial_data()

            with db.session() as session:
                # 既存のエントリーが保持されていることを確認
                entry = session.execute(
                    select(Entry).filter_by(user_id=admin_id, title='LifeLogの運営開始について')
                ).scalar_one()
                assert entry.content == '既存の内容です'
                assert entry.notes == '既存のノート'

    def test_create_initial_data_with_existing_diary_items(self, app):
        """既存の活動項目がある場合のテスト"""
        with app.app_context():
            # 先にユーザー、エントリー、活動項目を作成
            with db.session() as session:
                tetsu = User(
                    userid='tetsu',
                    name='devilman',
                    password='Tetsu3210',
                    created_at=datetime.now()
                )
                session.add(tetsu)
                session.commit()

                tetsu_id = tetsu.id

                entry = Entry(
                    user=tetsu,
                    title='試合に向けて本格始動',
                    content='既存の内容です',
                    notes='既存のノート',
                    created_at=datetime.now()
                )
                session.add(entry)
                session.commit()

                entry_id = entry.id

                existing_item = DiaryItem(
                    entry=entry,
                    item_name='既存の活動',
                    item_content='既存の活動内容',
                    created_at=datetime.now()
                )
                session.add(existing_item)
                session.commit()

            # 初期データを作成
            create_initial_data()

            with db.session() as session:
                # 既存の活動項目が保持されていることを確認
                entry = session.execute(
                    select(Entry).filter_by(user_id=tetsu_id, title='試合に向けて本格始動')
                ).scalar_one()
                diary_items = session.execute(
                    select(DiaryItem).filter_by(entry_id=entry_id)
                ).scalars().all()
                
                assert len(diary_items) == 1
                assert diary_items[0].item_name == '既存の活動'
                assert diary_items[0].item_content == '既存の活動内容'

    def test_create_initial_data_relationships(self, app):
        """リレーションシップの整合性テスト"""
        with app.app_context():
            create_initial_data()

            with db.session() as session:
                # ユーザーとエントリーの関連を確認
                admin = session.execute(select(User).filter_by(userid='admin')).scalar_one()
                tetsu = session.execute(select(User).filter_by(userid='tetsu')).scalar_one()

                assert len(admin.entries) == 1
                assert len(tetsu.entries) == 1

                # エントリーと活動項目の関連を確認
                tetsu_entry = tetsu.entries[0]
                assert len(tetsu_entry.items) == 2
                assert all(item.entry == tetsu_entry for item in tetsu_entry.items)

    def test_create_initial_data_attribute_values(self, app):
        """属性値の詳細な検証テスト"""
        with app.app_context():
            create_initial_data()

            with db.session() as session:
                # 管理者ユーザーの属性を確認
                admin = session.execute(select(User).filter_by(userid='admin')).scalar_one()
                assert admin.is_admin is True
                assert admin.is_locked is False
                assert admin.is_visible is True
                assert admin.login_attempts == 0
                assert isinstance(admin.created_at, datetime)

                # テストユーザーの属性を確認
                tetsu = session.execute(select(User).filter_by(userid='tetsu')).scalar_one()
                assert tetsu.is_admin is False
                assert tetsu.is_locked is False
                assert tetsu.is_visible is True
                assert tetsu.login_attempts == 0
                assert isinstance(tetsu.created_at, datetime)

                # エントリーの属性を確認
                admin_entry = admin.entries[0]
                assert isinstance(admin_entry.created_at, datetime)
                assert admin_entry.updated_at is None

                # 活動項目の属性を確認
                tetsu_entry = tetsu.entries[0]
                for item in tetsu_entry.items:
                    assert isinstance(item.created_at, datetime)
                    assert item.entry_id == tetsu_entry.id
