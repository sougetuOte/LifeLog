import pytest
from datetime import datetime, timedelta
from models.user import User
from models.entry import Entry
from database import db
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import text

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
        assert user.id is not None, "ユーザーIDが生成されていません"
        assert user.userid == 'test_user', "useridが正しくありません"
        assert user.name == 'Test User', "nameが正しくありません"
        assert user.password == 'password123', "passwordが正しくありません"
        assert isinstance(user.created_at, datetime), "created_atがdatetime型ではありません"
        
        # デフォルト値を検証
        assert user.is_admin is False, "is_adminのデフォルト値が正しくありません"
        assert user.is_locked is False, "is_lockedのデフォルト値が正しくありません"
        assert user.is_visible is True, "is_visibleのデフォルト値が正しくありません"
        assert user.login_attempts == 0, "login_attemptsのデフォルト値が正しくありません"
        assert user.last_login_attempt is None, "last_login_attemptのデフォルト値が正しくありません"

    def test_user_model_validation(self, app):
        """モデルレベルのバリデーションテスト"""
        # useridのバリデーション
        with pytest.raises(ValueError, match='User ID cannot be None'):
            User(name='Test', password='password123')

        with pytest.raises(ValueError, match='User ID must be a string'):
            User(userid=123, name='Test', password='password123')

        with pytest.raises(ValueError, match='User ID cannot be empty'):
            User(userid='', name='Test', password='password123')

        with pytest.raises(ValueError, match='User ID must be 20 characters or less'):
            User(userid='a' * 21, name='Test', password='password123')

        # nameのバリデーション
        with pytest.raises(ValueError, match='Name cannot be None'):
            User(userid='test', password='password123')

        with pytest.raises(ValueError, match='Name must be a string'):
            User(userid='test', name=123, password='password123')

        with pytest.raises(ValueError, match='Name cannot be empty'):
            User(userid='test', name='', password='password123')

        with pytest.raises(ValueError, match='Name must be 20 characters or less'):
            User(userid='test', name='a' * 21, password='password123')

        # passwordのバリデーション
        with pytest.raises(ValueError, match='Password cannot be None'):
            User(userid='test', name='Test')

        with pytest.raises(ValueError, match='Password must be a string'):
            User(userid='test', name='Test', password=123)

        with pytest.raises(ValueError, match='Password cannot be empty'):
            User(userid='test', name='Test', password='')

    def test_user_database_validation(self, app, session):
        """データベースレベルのバリデーションテスト"""
        # 重複するuseridのテスト
        user1 = User(
            userid='test_user',
            name='Test User 1',
            password='password123',
            created_at=datetime.now()
        )
        session.add(user1)
        session.flush()

        with pytest.raises(IntegrityError):
            user2 = User(
                userid='test_user',  # 重複するuserid
                name='Test User 2',
                password='password123',
                created_at=datetime.now()
            )
            session.add(user2)
            session.flush()
        session.rollback()

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
        assert len(user.entries) == 2, "エントリーの数が正しくありません"
        assert entry1 in user.entries, "Entry1が関連付けられていません"
        assert entry2 in user.entries, "Entry2が関連付けられていません"

    def test_user_cascade_delete(self, app, session):
        """ユーザー削除時のカスケード削除テスト"""
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
        entries = [
            Entry(
                user_id=user.id,
                title=f'Test Entry {i}',
                content=f'Content {i}',
                notes=f'Notes {i}'
            )
            for i in range(3)
        ]
        session.add_all(entries)
        session.flush()

        # エントリーIDを保存
        entry_ids = [entry.id for entry in entries]

        # ユーザーを削除
        session.delete(user)
        session.flush()
        
        # エントリーも削除されていることを確認
        for entry_id in entry_ids:
            assert session.query(Entry).filter_by(id=entry_id).first() is None, \
                f"Entry {entry_id}が削除されていません"

    def test_password_validation(self, app, session):
        """パスワード関連の機能テスト"""
        user = User(
            userid='test_user',
            name='Test User',
            password='correct_password',
            created_at=datetime.now()
        )

        # パスワードチェック - 基本ケース
        assert user.check_password('correct_password') is True, \
            "正しいパスワードが認証されません"
        assert user.check_password('wrong_password') is False, \
            "誤ったパスワードが認証されています"

        # パスワードチェック - エッジケース
        assert user.check_password('') is False, \
            "空のパスワードが認証されています"
        assert user.check_password(None) is False, \
            "Noneのパスワードが認証されています"
        assert user.check_password('   correct_password   ') is False, \
            "空白を含むパスワードが認証されています"

        # パスワードバリデーション - 基本ケース
        assert user.validate_password('correct_password') is True, \
            "正しいパスワードが検証されません"
        assert user.validate_password('wrong_password') is False, \
            "誤ったパスワードが検証されています"

        # パスワードバリデーション - エッジケース
        assert user.validate_password('') is False, \
            "空のパスワードが検証されています"
        assert user.validate_password(None) is False, \
            "Noneのパスワードが検証されています"
        assert user.validate_password('   correct_password   ') is False, \
            "空白を含むパスワードが検証されています"

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
        assert user.check_lock_status() is False, "初期状態でロックされています"
        assert user.login_attempts == 0, "初期状態でログイン試行回数が0ではありません"
        assert user.last_login_attempt is None, "初期状態で最終ログイン試行時刻が設定されています"

        # ログイン試行を増やす
        user.increment_login_attempts()
        first_attempt_time = user.last_login_attempt
        assert user.login_attempts == 1, "ログイン試行回数が正しく増加していません"
        assert user.last_login_attempt is not None, "最終ログイン試行時刻が設定されていません"
        assert user.check_lock_status() is False, "1回目の試行でロックされています"

        # 時間経過をシミュレート
        user.last_login_attempt = first_attempt_time + timedelta(minutes=1)
        user.increment_login_attempts()
        assert user.login_attempts == 2, "ログイン試行回数が正しく増加していません"
        assert user.check_lock_status() is False, "2回目の試行でロックされています"

        # 3回目の試行でロック
        user.last_login_attempt = first_attempt_time + timedelta(minutes=2)
        user.increment_login_attempts()
        assert user.login_attempts == 3, "ログイン試行回数が正しく増加していません"
        assert user.is_locked is True, "3回目の試行でロックされていません"
        assert user.check_lock_status() is True, "ロック状態が正しく検出されていません"

        # ロック状態での追加試行
        user.increment_login_attempts()
        assert user.login_attempts == 4, "ロック状態でログイン試行回数が増加していません"
        assert user.is_locked is True, "ロック状態が解除されています"
        assert user.check_lock_status() is True, "ロック状態が正しく検出されていません"

        # ログイン試行のリセット
        user.reset_login_attempts()
        assert user.login_attempts == 0, "ログイン試行回数がリセットされていません"
        assert user.last_login_attempt is None, "最終ログイン試行時刻がリセットされていません"
        assert user.is_locked is True, "ロック状態が解除されています"
        assert user.check_lock_status() is True, "ロック状態が正しく検出されていません"

    def test_find_by_userid(self, app, session):
        """ユーザー検索機能のテスト"""
        # 外部キー制約を有効化
        session.execute(text('PRAGMA foreign_keys = ON'))
        session.commit()

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
        assert found_user is not None, "可視ユーザーが見つかりません"
        assert found_user.userid == 'visible_user', "見つかったユーザーのIDが正しくありません"
        assert found_user.is_visible is True, "見つかったユーザーが可視状態ではありません"

        # 管理者ユーザーの検索
        found_admin = User.find_by_userid('admin_user')
        assert found_admin is not None, "管理者ユーザーが見つかりません"
        assert found_admin.userid == 'admin_user', "見つかった管理者のIDが正しくありません"
        assert found_admin.is_admin is True, "見つかったユーザーが管理者ではありません"

        # 非表示ユーザーは検索されない
        invisible_user = User.find_by_userid('invisible_user')
        assert invisible_user is None, "非表示ユーザーが検索されています"

        # 存在しないユーザー
        nonexistent_user = User.find_by_userid('nonexistent')
        assert nonexistent_user is None, "存在しないユーザーが検索されています"

        # 可視性の変更テスト
        user1.is_visible = False
        session.flush()
        assert User.find_by_userid('visible_user') is None, \
            "非表示に変更されたユーザーが検索されています"

    def test_user_repr(self, app):
        """ユーザーの文字列表現テスト"""
        test_cases = [
            # 通常のケース
            {
                'userid': 'test_user',
                'expected': '<User test_user>'
            },
            # 特殊文字を含むケース
            {
                'userid': 'test/user#2',
                'expected': '<User test/user#2>'
            },
            # 長いユーザーIDのケース
            {
                'userid': 'a' * 20,
                'expected': f'<User {"a" * 20}>'
            }
        ]

        for case in test_cases:
            user = User(
                userid=case['userid'],
                name='Test User',
                password='password123'
            )
            assert repr(user) == case['expected'], \
                f"ユーザーID '{case['userid']}' の文字列表現が正しくありません"
