import pytest
from datetime import datetime
from models.init_data import create_initial_data
from models.user import User
from models.entry import Entry
from models.diary_item import DiaryItem
from database import db

class TestInitData:
    def test_create_initial_data(self, app, session):
        """初期データ作成のテスト"""
        # 初期データを作成
        create_initial_data()

        # ユーザーの検証
        users = session.query(User).all()
        assert len(users) == 3
        
        admin = session.query(User).filter_by(userid='admin').first()
        assert admin is not None
        assert admin.name == '管理人'
        assert admin.is_admin is True
        assert admin.check_password('Admin3210')

        tetsu = session.query(User).filter_by(userid='tetsu').first()
        assert tetsu is not None
        assert tetsu.name == 'devilman'
        assert tetsu.is_admin is False
        assert tetsu.check_password('Tetsu3210')

        gento = session.query(User).filter_by(userid='gento').first()
        assert gento is not None
        assert gento.name == 'gen chan'
        assert gento.is_admin is False
        assert gento.check_password('Gento3210')

        # エントリーの検証
        entries = session.query(Entry).all()
        assert len(entries) == 2

        admin_entry = session.query(Entry).filter_by(user_id=admin.id).first()
        assert admin_entry is not None
        assert admin_entry.title == 'LifeLogの運営開始について'
        assert 'LifeLogの運営を開始しました' in admin_entry.content
        assert '天気：晴れ' in admin_entry.notes

        tetsu_entry = session.query(Entry).filter_by(user_id=tetsu.id).first()
        assert tetsu_entry is not None
        assert tetsu_entry.title == '試合に向けて本格始動'
        assert '本格的なトレーニング期間' in tetsu_entry.content
        assert '体重：75kg' in tetsu_entry.notes

        # DiaryItemの検証
        diary_items = session.query(DiaryItem).filter_by(entry_id=tetsu_entry.id).all()
        assert len(diary_items) == 2

        training_item = next((item for item in diary_items if item.item_name == '筋トレ'), None)
        assert training_item is not None
        assert 'スクワット' in training_item.item_content
        assert 'ベンチプレス' in training_item.item_content

        running_item = next((item for item in diary_items if item.item_name == 'ランニング'), None)
        assert running_item is not None
        assert '朝：10km' in running_item.item_content
        assert '夜：5km' in running_item.item_content

    def test_create_initial_data_idempotency(self, app, session):
        """初期データ作成の冪等性テスト"""
        # 2回実行しても問題ないことを確認
        create_initial_data()
        create_initial_data()

        # ユーザー数が3のままであることを確認
        users = session.query(User).all()
        assert len(users) == 3

        # エントリー数が2のままであることを確認
        entries = session.query(Entry).all()
        assert len(entries) == 2

        # DiaryItem数が2のままであることを確認
        diary_items = session.query(DiaryItem).all()
        assert len(diary_items) == 2
