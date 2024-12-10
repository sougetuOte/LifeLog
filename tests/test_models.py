import pytest
from datetime import datetime
from sqlalchemy.orm import DeclarativeBase
from models import Base, User, Entry, DiaryItem, create_initial_data
from database import db

class TestBase:
    def test_base_inheritance(self):
        """Baseクラスの継承関係テスト"""
        assert issubclass(Base, DeclarativeBase)

class TestModels:
    def setup_method(self):
        """各テストメソッドの前にデータベースをクリア"""
        with db.session() as session:
            session.query(DiaryItem).delete()
            session.query(Entry).delete()
            session.query(User).delete()
            session.commit()

    def test_create_initial_data(self, app):
        """初期データ作成機能のテスト"""
        with app.app_context():
            create_initial_data()

            with db.session() as session:
                # ユーザーの確認
                users = session.query(User).all()
                assert len(users) == 3

                admin = session.query(User).filter_by(userid='admin').first()
                assert admin.name == '管理人'
                assert admin.is_admin is True
                assert admin.password == 'Admin3210'

                tetsu = session.query(User).filter_by(userid='tetsu').first()
                assert tetsu.name == 'devilman'
                assert tetsu.password == 'Tetsu3210'

                gento = session.query(User).filter_by(userid='gento').first()
                assert gento.name == 'gen chan'
                assert gento.password == 'Gento3210'

                # エントリーの確認
                entries = session.query(Entry).all()
                assert len(entries) == 2

                admin_entry = session.query(Entry).filter_by(user=admin).first()
                assert admin_entry.title == 'LifeLogの運営開始について'
                assert '本日よりLifeLogの運営を開始しました' in admin_entry.content
                assert '天気：晴れ' in admin_entry.notes

                tetsu_entry = session.query(Entry).filter_by(user=tetsu).first()
                assert tetsu_entry.title == '試合に向けて本格始動'
                assert '本格的なトレーニング期間' in tetsu_entry.content
                assert '体重：75kg' in tetsu_entry.notes

                # 活動項目の確認
                diary_items = session.query(DiaryItem).filter_by(entry=tetsu_entry).all()
                assert len(diary_items) == 2

                training_item = next(item for item in diary_items if item.item_name == '筋トレ')
                assert 'スクワット' in training_item.item_content
                assert 'ベンチプレス' in training_item.item_content

                running_item = next(item for item in diary_items if item.item_name == 'ランニング')
                assert '朝：10km' in running_item.item_content
                assert '夜：5km' in running_item.item_content

    def test_model_relationships(self, app):
        """モデル間のリレーションシップテスト"""
        with app.app_context():
            create_initial_data()

            with db.session() as session:
                # ユーザーとエントリーの関連
                admin = session.query(User).filter_by(userid='admin').first()
                tetsu = session.query(User).filter_by(userid='tetsu').first()

                assert len(admin.entries) == 1
                assert len(tetsu.entries) == 1

                # エントリーとユーザーの関連
                admin_entry = admin.entries[0]
                assert admin_entry.user == admin

                tetsu_entry = tetsu.entries[0]
                assert tetsu_entry.user == tetsu

                # エントリーと活動項目の関連
                assert len(tetsu_entry.items) == 2
                for item in tetsu_entry.items:
                    assert item.entry == tetsu_entry

    def test_model_timestamps(self, app):
        """タイムスタンプフィールドのテスト"""
        with app.app_context():
            create_initial_data()

            with db.session() as session:
                # ユーザーのタイムスタンプ
                admin = session.query(User).filter_by(userid='admin').first()
                assert isinstance(admin.created_at, datetime)

                # エントリーのタイムスタンプ
                entry = admin.entries[0]
                assert isinstance(entry.created_at, datetime)
                assert entry.updated_at is None

                # 活動項目のタイムスタンプ
                tetsu = session.query(User).filter_by(userid='tetsu').first()
                tetsu_entry = tetsu.entries[0]
                for item in tetsu_entry.items:
                    assert isinstance(item.created_at, datetime)

    def test_model_repr(self, app):
        """__repr__メソッドのテスト"""
        with app.app_context():
            create_initial_data()

            with db.session() as session:
                # Userの__repr__
                admin = session.query(User).filter_by(userid='admin').first()
                assert repr(admin) == '<User admin>'

                # Entryの__repr__
                entry = admin.entries[0]
                assert repr(entry) == '<Entry LifeLogの運営開始について>'

                # DiaryItemの__repr__
                tetsu = session.query(User).filter_by(userid='tetsu').first()
                item = tetsu.entries[0].items[0]
                assert repr(item) == f'<DiaryItem {item.item_name}>'
