import pytest
from datetime import datetime, timedelta
from models.user import User
from models.entry import Entry
from database import db

class TestUser:
    def test_user_creation(self, app, session):
        """ユーザーの基本的な作成テスト"""
        user = User(
            userid='test_user',
            name='Test User',
            password='password123',
            created_at=datetime.now()
        )
        session.add(user)
        session.flush()

        # 基本的な属性を検証
        assert user.id is not None
        assert user.userid == 'test_user'
        assert user.name == 'Test User'
        assert user.password == 'password123'
        assert isinstance(user.created_at, datetime)
        
        # デフォルト値を検証
        assert user.is_admin is False
        assert user.is_locked is False
        assert user.is_visible is True
        assert user.login_attempts == 0
        assert user.last_login_attempt is None

    def test_user_relationships(self, app, session):
        """ユーザーのリレーションシップテスト"""
        # ユーザーを作成
        user = User(
            userid='test_user',
            name='Test User',
            password='password123',
            created_at=datetime.now()
        )
        session.add(user)
        session.flush()

        # エントリーを追加
        entry1 = Entry(
            user_id=user.id,
            title='Test Entry 1',
            content='Content 1',
            notes='Notes 1'
        )
        entry2 = Entry(
            user_id=user.id,
            title='Test Entry 2',
            content='Content 2',
            notes='Notes 2'
        )
        session.add_all([entry1, entry2])
        session.flush()

        # リレーションシップを検証
        assert len(user.entries) == 2
        assert entry1 in user.entries
        assert entry2 in user.entries

        # cascade deleteのテスト
        session.delete(user)
        session.flush()
        
        # エントリーも削除されていることを確認
        assert session.query(Entry).filter_by(id=entry1.id).first() is None
        assert session.query(Entry).filter_by(id=entry2.id).first() is None

    def test_password_validation(self, app, session):
        """パスワード関連の機能テスト"""
        user = User(
            userid='test_user',
            name='Test User',
            password='correct_password',
            created_at=datetime.now()
        )

        # パスワードチェック - 基本ケース
        assert user.check_password('correct_password') is True
        assert user.check_password('wrong_password') is False

        # パスワードチェック - エッジケース
        assert user.check_password('') is False
        assert user.check_password(None) is False
        assert user.check_password('   correct_password   ') is False  # 空白を含む

        # パスワードバリデーション - 基本ケース
        assert user.validate_password('correct_password') is True
        assert user.validate_password('wrong_password') is False

        # パスワードバリデーション - エッジケース
        assert user.validate_password('') is False
        assert user.validate_password(None) is False
        assert user.validate_password('   correct_password   ') is False

    def test_lock_mechanism(self, app, session):
        """アカウントロック機能のテスト"""
        user = User(
            userid='test_user',
            name='Test User',
            password='password123',
            created_at=datetime.now()
        )
        session.add(user)
        session.flush()

        # 初期状態の確認
        assert user.check_lock_status() is False
        assert user.login_attempts == 0
        assert user.last_login_attempt is None

        # ログイン試行を増やす
        user.increment_login_attempts()
        first_attempt_time = user.last_login_attempt
        assert user.login_attempts == 1
        assert user.last_login_attempt is not None
        assert user.check_lock_status() is False

        # 時間経過をシミュレート
        user.last_login_attempt = first_attempt_time + timedelta(minutes=1)
        user.increment_login_attempts()
        assert user.login_attempts == 2
        assert user.check_lock_status() is False

        # 3回目の試行でロック
        user.last_login_attempt = first_attempt_time + timedelta(minutes=2)
        user.increment_login_attempts()
        assert user.login_attempts == 3
        assert user.is_locked is True
        assert user.check_lock_status() is True

        # ロック状態での追加試行
        user.increment_login_attempts()
        assert user.login_attempts == 4
        assert user.is_locked is True
        assert user.check_lock_status() is True

        # ログイン試行のリセット
        user.reset_login_attempts()
        assert user.login_attempts == 0
        assert user.last_login_attempt is None
        # ただし、is_lockedはリセットされない
        assert user.is_locked is True
        assert user.check_lock_status() is True

    def test_find_by_userid(self, app, session):
        """ユーザー検索機能のテスト"""
        # 通常のユーザーを作成
        user1 = User(
            userid='visible_user',
            name='Visible User',
            password='password123',
            is_visible=True,
            created_at=datetime.now()
        )
        
        # 非表示のユーザーを作成
        user2 = User(
            userid='invisible_user',
            name='Invisible User',
            password='password123',
            is_visible=False,
            created_at=datetime.now()
        )

        # 管理者ユーザーを作成
        admin = User(
            userid='admin_user',
            name='Admin User',
            password='admin123',
            is_admin=True,
            is_visible=True,
            created_at=datetime.now()
        )
        
        session.add_all([user1, user2, admin])
        session.flush()

        # 通常ユーザーの検索
        found_user = User.find_by_userid('visible_user')
        assert found_user is not None
        assert found_user.userid == 'visible_user'
        assert found_user.is_visible is True

        # 管理者ユーザーの検索
        found_admin = User.find_by_userid('admin_user')
        assert found_admin is not None
        assert found_admin.userid == 'admin_user'
        assert found_admin.is_admin is True

        # 非表示ユーザーは検索されない
        invisible_user = User.find_by_userid('invisible_user')
        assert invisible_user is None

        # 存在しないユーザー
        nonexistent_user = User.find_by_userid('nonexistent')
        assert nonexistent_user is None

        # 可視性の変更テスト
        user1.is_visible = False
        session.flush()
        assert User.find_by_userid('visible_user') is None

    def test_user_repr(self, app, session):
        """ユーザーの__repr__メソッドのテスト"""
        # 通常のケース
        user = User(
            userid='test_user',
            name='Test User',
            password='password123'
        )
        assert repr(user) == '<User test_user>'

        # 特殊文字を含むケース
        user2 = User(
            userid='test/user#2',
            name='Test User 2',
            password='password123'
        )
        assert repr(user2) == '<User test/user#2>'

        # 長いユーザーIDのケース
        long_userid = 'a' * 20  # 最大長
        user3 = User(
            userid=long_userid,
            name='Test User 3',
            password='password123'
        )
        assert repr(user3) == f'<User {long_userid}>'
