import pytest
import time
from datetime import datetime, timedelta
from models.user import User
from models.entry import Entry
from database import db

class TestUser:
    def setup_method(self):
        """各テストメソッドの前にデータベースをクリア"""
        with db.session() as session:
            session.query(Entry).delete()
            session.query(User).delete()
            session.commit()

    def teardown_method(self):
        """各テストメソッドの後にデータベースをクリア"""
        with db.session() as session:
            session.query(Entry).delete()
            session.query(User).delete()
            session.commit()

    def test_create_user_with_valid_data(self, app):
        """有効なデータでのUser作成テスト"""
        with app.app_context():
            user = User(
                userid='testuser',
                name='Test User',
                password='TestPass123'
            )
            assert user.userid == 'testuser'
            assert user.name == 'Test User'
            assert user.password == 'TestPass123'
            assert not user.is_admin
            assert not user.is_locked
            assert user.is_visible
            assert user.login_attempts == 0
            assert user.last_login_attempt is None
            assert isinstance(user.created_at, datetime)

    def test_create_user_without_required_fields(self, app):
        """必須フィールドなしでのUser作成テスト"""
        with app.app_context():
            # useridなし
            with pytest.raises(ValueError, match='User ID cannot be None'):
                User(
                    name='Test User',
                    password='TestPass123'
                )

            # nameなし
            with pytest.raises(ValueError, match='Name cannot be None'):
                User(
                    userid='testuser',
                    password='TestPass123'
                )

            # passwordなし
            with pytest.raises(ValueError, match='Password cannot be None'):
                User(
                    userid='testuser',
                    name='Test User'
                )

    def test_validate_userid(self, app):
        """useridのバリデーションテスト"""
        with app.app_context():
            # 数値の場合
            with pytest.raises(ValueError, match='User ID must be a string'):
                User(
                    userid=123,
                    name='Test User',
                    password='TestPass123'
                )

            # 空文字の場合
            with pytest.raises(ValueError, match='User ID cannot be empty'):
                User(
                    userid='',
                    name='Test User',
                    password='TestPass123'
                )

            # スペースのみの場合
            with pytest.raises(ValueError, match='User ID cannot be empty'):
                User(
                    userid='   ',
                    name='Test User',
                    password='TestPass123'
                )

            # 20文字を超える場合
            with pytest.raises(ValueError, match='User ID must be 20 characters or less'):
                User(
                    userid='a' * 21,
                    name='Test User',
                    password='TestPass123'
                )

    def test_validate_name(self, app):
        """nameのバリデーションテスト"""
        with app.app_context():
            # 数値の場合
            with pytest.raises(ValueError, match='Name must be a string'):
                User(
                    userid='testuser',
                    name=123,
                    password='TestPass123'
                )

            # 空文字の場合
            with pytest.raises(ValueError, match='Name cannot be empty'):
                User(
                    userid='testuser',
                    name='',
                    password='TestPass123'
                )

            # スペースのみの場合
            with pytest.raises(ValueError, match='Name cannot be empty'):
                User(
                    userid='testuser',
                    name='   ',
                    password='TestPass123'
                )

            # 20文字を超える場合
            with pytest.raises(ValueError, match='Name must be 20 characters or less'):
                User(
                    userid='testuser',
                    name='a' * 21,
                    password='TestPass123'
                )

    def test_validate_password(self, app):
        """passwordのバリデーションテスト"""
        with app.app_context():
            # 数値の場合
            with pytest.raises(ValueError, match='Password must be a string'):
                User(
                    userid='testuser',
                    name='Test User',
                    password=123
                )

            # 空文字の場合
            with pytest.raises(ValueError, match='Password cannot be empty'):
                User(
                    userid='testuser',
                    name='Test User',
                    password=''
                )

            # スペースのみの場合
            with pytest.raises(ValueError, match='Password cannot be empty'):
                User(
                    userid='testuser',
                    name='Test User',
                    password='   '
                )

    def test_check_password(self, app):
        """パスワードチェック機能のテスト"""
        with app.app_context():
            user = User(
                userid='testuser',
                name='Test User',
                password='TestPass123'
            )
            assert user.check_password('TestPass123')
            assert not user.check_password('WrongPass')

    def test_validate_password_method(self, app):
        """パスワードバリデーションメソッドのテスト"""
        with app.app_context():
            user = User(
                userid='testuser',
                name='Test User',
                password='TestPass123'
            )
            assert user.validate_password('correct_password')
            assert not user.validate_password('wrong_password')

    def test_check_lock_status(self, app):
        """ロック状態チェック機能のテスト"""
        with app.app_context():
            user = User(
                userid='testuser',
                name='Test User',
                password='TestPass123'
            )
            
            # 初期状態
            assert not user.check_lock_status()

            # ログイン試行回数による自動ロック
            user.login_attempts = 3
            assert user.check_lock_status()

            # 手動ロック
            user.login_attempts = 0
            user.is_locked = True
            assert user.check_lock_status()

    def test_increment_login_attempts(self, app):
        """ログイン試行回数インクリメント機能のテスト"""
        with app.app_context():
            user = User(
                userid='testuser',
                name='Test User',
                password='TestPass123'
            )
            
            assert user.login_attempts == 0
            assert not user.is_locked
            assert user.last_login_attempt is None

            # 1回目の試行
            user.increment_login_attempts()
            assert user.login_attempts == 1
            assert not user.is_locked
            assert isinstance(user.last_login_attempt, datetime)

            # 2回目の試行
            user.increment_login_attempts()
            assert user.login_attempts == 2
            assert not user.is_locked

            # 3回目の試行（ロック）
            user.increment_login_attempts()
            assert user.login_attempts == 3
            assert user.is_locked

    def test_reset_login_attempts(self, app):
        """ログイン試行回数リセット機能のテスト"""
        with app.app_context():
            user = User(
                userid='testuser',
                name='Test User',
                password='TestPass123'
            )
            
            # ログイン試行を増やす
            user.login_attempts = 2
            user.last_login_attempt = datetime.now()

            # リセット
            user.reset_login_attempts()
            assert user.login_attempts == 0
            assert user.last_login_attempt is None

    def test_find_by_userid(self, app):
        """ユーザーID検索機能のテスト"""
        with app.app_context():
            with db.session() as session:
                # テストユーザーを作成
                user1 = User(
                    userid='visible_user',
                    name='Visible User',
                    password='Pass123',
                    is_visible=True
                )
                user2 = User(
                    userid='invisible_user',
                    name='Invisible User',
                    password='Pass123',
                    is_visible=False
                )
                session.add(user1)
                session.add(user2)
                session.commit()

                # 可視ユーザーの検索
                found_user = User.find_by_userid('visible_user')
                assert found_user is not None
                assert found_user.userid == 'visible_user'

                # 不可視ユーザーの検索
                found_user = User.find_by_userid('invisible_user')
                assert found_user is None

                # 存在しないユーザーの検索
                found_user = User.find_by_userid('nonexistent')
                assert found_user is None

    def test_relationship_with_entries(self, app):
        """Entriesとのリレーションシップテスト"""
        with app.app_context():
            with db.session() as session:
                # ユーザーを作成
                user = User(
                    userid='testuser',
                    name='Test User',
                    password='TestPass123'
                )
                session.add(user)
                session.commit()

                # エントリーを追加
                entry1 = Entry(
                    user_id=user.id,
                    title='Entry 1',
                    content='Content 1'
                )
                entry2 = Entry(
                    user_id=user.id,
                    title='Entry 2',
                    content='Content 2'
                )
                session.add(entry1)
                session.add(entry2)
                session.commit()

                # リレーションシップを確認
                assert len(user.entries) == 2
                assert entry1 in user.entries
                assert entry2 in user.entries

                # cascade deleteのテスト
                session.delete(user)
                session.commit()

                # エントリーも削除されていることを確認
                entries = session.query(Entry).all()
                assert len(entries) == 0

    def test_repr(self, app):
        """__repr__メソッドのテスト"""
        with app.app_context():
            user = User(
                userid='testuser',
                name='Test User',
                password='TestPass123'
            )
            assert repr(user) == '<User testuser>'

    def test_user_lock_unlock_state_transitions(self, app):
        """ユーザーのロック/アンロック状態遷移テスト"""
        with app.app_context():
            with db.session() as session:
                user = User(
                    userid='testuser',
                    name='Test User',
                    password='TestPass123'
                )
                session.add(user)
                session.commit()

                # 初期状態
                assert not user.is_locked
                assert user.login_attempts == 0

                # ロック状態への遷移（手動）
                user.is_locked = True
                session.commit()
                assert user.is_locked
                assert user.check_lock_status()

                # アンロック状態への遷移
                user.is_locked = False
                user.login_attempts = 0
                session.commit()
                assert not user.is_locked
                assert not user.check_lock_status()

                # ロック状態への遷移（自動：ログイン試行回数超過）
                for _ in range(3):
                    user.increment_login_attempts()
                session.commit()
                assert user.is_locked
                assert user.check_lock_status()
                assert user.login_attempts == 3

    def test_login_attempts_with_timestamp(self, app):
        """ログイン試行回数と最終試行時刻のテスト"""
        with app.app_context():
            with db.session() as session:
                user = User(
                    userid='testuser',
                    name='Test User',
                    password='TestPass123'
                )
                session.add(user)
                session.commit()

                # 初期状態
                assert user.last_login_attempt is None

                # 1回目の試行
                user.increment_login_attempts()
                session.commit()
                first_attempt_time = user.last_login_attempt
                assert first_attempt_time is not None

                # 少し待機
                time.sleep(0.1)

                # 2回目の試行
                user.increment_login_attempts()
                session.commit()
                second_attempt_time = user.last_login_attempt
                assert second_attempt_time > first_attempt_time

                # リセット
                user.reset_login_attempts()
                session.commit()
                assert user.last_login_attempt is None

    def test_find_users_by_criteria(self, app):
        """複数条件でのユーザー検索テスト"""
        with app.app_context():
            with db.session() as session:
                # テストユーザーを作成
                admin_user = User(
                    userid='admin',
                    name='Admin User',
                    password='Pass123',
                    is_admin=True,
                    is_visible=True
                )
                normal_user = User(
                    userid='normal',
                    name='Normal User',
                    password='Pass123',
                    is_admin=False,
                    is_visible=True
                )
                locked_user = User(
                    userid='locked',
                    name='Locked User',
                    password='Pass123',
                    is_admin=False,
                    is_visible=True,
                    is_locked=True
                )
                invisible_user = User(
                    userid='invisible',
                    name='Invisible User',
                    password='Pass123',
                    is_admin=False,
                    is_visible=False
                )
                session.add_all([admin_user, normal_user, locked_user, invisible_user])
                session.commit()

                # 管理者ユーザーの検索
                admin_users = session.query(User).filter_by(is_admin=True).all()
                assert len(admin_users) == 1
                assert admin_users[0].userid == 'admin'

                # 可視ユーザーの検索
                visible_users = session.query(User).filter_by(is_visible=True).all()
                assert len(visible_users) == 3
                assert all(user.is_visible for user in visible_users)

                # ロックされたユーザーの検索
                locked_users = session.query(User).filter_by(is_locked=True).all()
                assert len(locked_users) == 1
                assert locked_users[0].userid == 'locked'

                # 通常の可視ユーザーの検索（管理者でもロックされてもいない）
                normal_users = session.query(User).filter_by(
                    is_admin=False,
                    is_locked=False,
                    is_visible=True
                ).all()
                assert len(normal_users) == 1
                assert normal_users[0].userid == 'normal'
