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

            # ユーザーの確認
            admin = db.session.execute(select(User).filter_by(userid='admin')).scalar_one()
            assert admin.name == '管理人'
            assert admin.is_admin is True

            tetsu = db.session.execute(select(User).filter_by(userid='tetsu')).scalar_one()
            assert tetsu.name == 'devilman'
            assert tetsu.is_admin is False

            gento = db.session.execute(select(User).filter_by(userid='gento')).scalar_one()
            assert gento.name == 'gen chan'
            assert gento.is_admin is False

            # 投稿の確認
            admin_entry = db.session.execute(
                select(Entry).filter_by(user_id=admin.id, title='LifeLogの運営開始について')
            ).scalar_one()
            assert 'LifeLogの運営を開始しました' in admin_entry.content
            assert admin_entry.user == admin

            tetsu_entry = db.session.execute(
                select(Entry).filter_by(user_id=tetsu.id, title='試合に向けて本格始動')
            ).scalar_one()
            assert '本格的なトレーニング期間' in tetsu_entry.content
            assert tetsu_entry.user == tetsu

            # DiaryItemの確認
            diary_items = db.session.execute(
                select(DiaryItem).filter_by(entry_id=tetsu_entry.id)
            ).scalars().all()
            assert len(diary_items) == 2
            
            training_item = next(item for item in diary_items if item.item_name == '筋トレ')
            assert 'スクワット' in training_item.item_content
            assert training_item.entry == tetsu_entry

            running_item = next(item for item in diary_items if item.item_name == 'ランニング')
            assert '10km' in running_item.item_content
            assert running_item.entry == tetsu_entry

    def test_create_initial_data_idempotency(self, app):
        """初期データ作成の冪等性テスト"""
        with app.app_context():
            # 2回実行しても問題ないことを確認
            create_initial_data()
            
            # ユーザー数を記録
            user_count_1 = len(db.session.execute(select(User)).scalars().all())
            entry_count_1 = len(db.session.execute(select(Entry)).scalars().all())
            item_count_1 = len(db.session.execute(select(DiaryItem)).scalars().all())

            create_initial_data()

            # 2回目実行後も同じ数であることを確認
            user_count_2 = len(db.session.execute(select(User)).scalars().all())
            entry_count_2 = len(db.session.execute(select(Entry)).scalars().all())
            item_count_2 = len(db.session.execute(select(DiaryItem)).scalars().all())

            assert user_count_1 == user_count_2
            assert entry_count_1 == entry_count_2
            assert item_count_1 == item_count_2

    def test_create_initial_data_with_existing_users(self, app):
        """既存ユーザーがいる場合のテスト"""
        with app.app_context():
            # 先に管理者ユーザーを作成
            admin = User(
                userid='admin',
                name='既存管理者',
                password='ExistingAdmin123',
                is_admin=True,
                is_locked=False,
                is_visible=True,
                login_attempts=0,
                created_at=datetime.now()
            )
            db.session.add(admin)
            db.session.commit()

            # 初期データを作成
            create_initial_data()

            # 既存の管理者が上書きされていないことを確認
            admin = db.session.execute(select(User).filter_by(userid='admin')).scalar_one()
            assert admin.name == '既存管理者'
            assert admin.password == 'ExistingAdmin123'

    def test_create_initial_data_with_partial_data(self, app):
        """一部のデータのみ存在する場合のテスト"""
        with app.app_context():
            # tetsuユーザーのみ先に作成
            tetsu = User(
                userid='tetsu',
                name='existing tetsu',
                password='ExistingTetsu123',
                is_admin=False,
                is_locked=False,
                is_visible=True,
                login_attempts=0,
                created_at=datetime.now()
            )
            db.session.add(tetsu)
            db.session.commit()

            # 初期データを作成
            create_initial_data()

            # tetsuユーザーが保持され、他のデータが作成されていることを確認
            tetsu = db.session.execute(select(User).filter_by(userid='tetsu')).scalar_one()
            assert tetsu.name == 'existing tetsu'

            admin = db.session.execute(select(User).filter_by(userid='admin')).scalar_one()
            assert admin.name == '管理人'

            gento = db.session.execute(select(User).filter_by(userid='gento')).scalar_one()
            assert gento.name == 'gen chan'

    def test_create_initial_data_error_handling(self, app):
        """エラーハンドリングのテスト"""
        with app.app_context():
            # 無効なユーザーを作成してエラーを発生させる
            with pytest.raises(ValueError, match='Name must be a string'):
                User(
                    userid='test',
                    name=None,  # 無効な名前
                    password='password',
                    is_admin=False,
                    is_locked=False,
                    is_visible=True,
                    login_attempts=0,
                    created_at=datetime.now()
                )

            # 正常に初期データを作成できることを確認
            create_initial_data()
            admin = db.session.execute(select(User).filter_by(userid='admin')).scalar_one()
            assert admin.name == '管理人'
