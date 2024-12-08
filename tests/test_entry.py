# tests/test_entry.py
import pytest
from datetime import datetime
from models.entry import Entry
from models.user import User

class TestEntry:
    def test_entry_creation(self, session):
        # テストユーザーの作成
        user = User(
            userid="test_user",
            name="Test User",
            password="Test1234",
            created_at=datetime.now()
        )
        session.add(user)
        session.commit()

        # エントリーの作成
        entry = Entry(
            user_id=user.id,
            title="Test Title",
            content="Test Content",
            notes="Test Notes",
            created_at=datetime.now()
        )
        session.add(entry)
        session.commit()

        saved_entry = session.get(Entry, entry.id)
        assert saved_entry.title == "Test Title"
        assert saved_entry.content == "Test Content"
        assert saved_entry.notes == "Test Notes"

    def test_entry_validation(self, session):
        # テストユーザーの作成
        user = User(
            userid="test_user",
            name="Test User",
            password="Test1234",
            created_at=datetime.now()
        )
        session.add(user)
        session.commit()

        # タイトルの長さ制限のテスト
        with pytest.raises(ValueError):
            entry = Entry(
                user_id=user.id,
                title="A" * 101,  # 100文字制限を超える
                content="Test Content",
                created_at=datetime.now()
            )
            session.add(entry)
            session.commit()

    def test_entry_update(self, session):
        # テストユーザーの作成
        user = User(
            userid="test_user",
            name="Test User",
            password="Test1234",
            created_at=datetime.now()
        )
        session.add(user)
        session.commit()

        # エントリーの作成と更新
        entry = Entry(
            user_id=user.id,
            title="Original Title",
            content="Original Content",
            created_at=datetime.now()
        )
        session.add(entry)
        session.commit()

        entry.update(title="Updated Title")
        session.commit()

        updated_entry = session.get(Entry, entry.id)
        assert updated_entry.title == "Updated Title"
        assert updated_entry.content == "Original Content"
        assert updated_entry.updated_at is not None
