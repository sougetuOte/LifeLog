import pytest
from datetime import datetime
from models.entry import Entry
from models.user import User
from models.diary_item import DiaryItem
from database import db
from sqlalchemy import text

@pytest.fixture(autouse=True)
def cleanup_database(app):
    """各テストの前にデータベースをクリーンアップ"""
    db.session.execute(text('DELETE FROM diary_items'))
    db.session.execute(text('DELETE FROM entries'))
    db.session.execute(text('DELETE FROM users'))
    db.session.commit()
    yield

@pytest.fixture
def test_user(app):
    """テストユーザーのフィクスチャ"""
    user = User(
        userid="testuser",
        name="Test User",
        password="password123",
        is_admin=False,
        is_visible=True
    )
    db.session.add(user)
    db.session.commit()
    return user

def test_entry_init():
    """エントリーの初期化テスト"""
    # 最小限の引数で初期化
    entry = Entry(user_id=1, title="Test Title", content="Test Content")
    assert entry.title == "Test Title"
    assert entry.content == "Test Content"
    assert entry.notes == ""  # デフォルト値
    assert isinstance(entry.created_at, datetime)
    assert entry.updated_at is None

    # 全ての引数を指定
    now = datetime.now()
    entry = Entry(
        user_id=1,
        title="Test Title",
        content="Test Content",
        notes="Test Notes",
        created_at=now
    )
    assert entry.title == "Test Title"
    assert entry.content == "Test Content"
    assert entry.notes == "Test Notes"
    assert entry.created_at == now

def test_entry_repr():
    """__repr__のテスト"""
    entry = Entry(user_id=1, title="Test Title", content="Test Content")
    assert repr(entry) == "<Entry Test Title>"

def test_validate_title():
    """タイトルのバリデーションテスト"""
    # 正常なタイトル
    entry = Entry(user_id=1, title="Valid Title", content="Test Content")
    assert entry.title == "Valid Title"

    # 無効なタイトル
    with pytest.raises(ValueError, match="Title cannot be None"):
        Entry(user_id=1, title=None, content="Test Content")

    with pytest.raises(ValueError, match="Title must be a string"):
        Entry(user_id=1, title=123, content="Test Content")

    with pytest.raises(ValueError, match="Title cannot be empty"):
        Entry(user_id=1, title="", content="Test Content")

    with pytest.raises(ValueError, match="Title cannot be empty"):
        Entry(user_id=1, title="   ", content="Test Content")

    with pytest.raises(ValueError, match="Title must be 100 characters or less"):
        Entry(user_id=1, title="a" * 101, content="Test Content")

def test_validate_content():
    """コンテンツのバリデーションテスト"""
    # 正常なコンテンツ
    entry = Entry(user_id=1, title="Test Title", content="Valid Content")
    assert entry.content == "Valid Content"

    # 無効なコンテンツ
    with pytest.raises(ValueError, match="Content cannot be None"):
        Entry(user_id=1, title="Test Title", content=None)

    with pytest.raises(ValueError, match="Content must be a string"):
        Entry(user_id=1, title="Test Title", content=123)

    with pytest.raises(ValueError, match="Content cannot be empty"):
        Entry(user_id=1, title="Test Title", content="")

    with pytest.raises(ValueError, match="Content cannot be empty"):
        Entry(user_id=1, title="Test Title", content="   ")

def test_validate_notes():
    """ノートのバリデーションテスト"""
    # 正常なノート
    entry = Entry(user_id=1, title="Test Title", content="Test Content", notes="Valid Notes")
    assert entry.notes == "Valid Notes"

    # 空のノート
    entry = Entry(user_id=1, title="Test Title", content="Test Content", notes="")
    assert entry.notes == ""

    # Noneの場合は空文字に変換
    entry = Entry(user_id=1, title="Test Title", content="Test Content", notes=None)
    assert entry.notes == ""

    # 無効なノート
    with pytest.raises(ValueError, match="Notes must be a string"):
        Entry(user_id=1, title="Test Title", content="Test Content", notes=123)

def test_validate_user_id():
    """ユーザーIDのバリデーションテスト"""
    # 正常なユーザーID
    entry = Entry(user_id=1, title="Test Title", content="Test Content")
    assert entry.user_id == 1

    # 無効なユーザーID
    with pytest.raises(ValueError, match="User ID cannot be None"):
        Entry(user_id=None, title="Test Title", content="Test Content")

    with pytest.raises(ValueError, match="User ID must be an integer"):
        Entry(user_id="1", title="Test Title", content="Test Content")

    with pytest.raises(ValueError, match="User ID must be positive"):
        Entry(user_id=0, title="Test Title", content="Test Content")

    with pytest.raises(ValueError, match="User ID must be positive"):
        Entry(user_id=-1, title="Test Title", content="Test Content")

def test_update(test_user):
    """更新メソッドのテスト"""
    # エントリーを作成
    entry = Entry(
        user_id=test_user.id,
        title="Original Title",
        content="Original Content",
        notes="Original Notes"
    )
    db.session.add(entry)
    db.session.commit()

    # 更新前の状態を確認
    assert entry.title == "Original Title"
    assert entry.content == "Original Content"
    assert entry.notes == "Original Notes"
    assert entry.updated_at is None

    # 更新を実行
    entry.update(
        title="Updated Title",
        content="Updated Content",
        notes="Updated Notes"
    )
    db.session.commit()

    # 更新後の状態を確認
    assert entry.title == "Updated Title"
    assert entry.content == "Updated Content"
    assert entry.notes == "Updated Notes"
    assert isinstance(entry.updated_at, datetime)

def test_relationships(test_user):
    """リレーションシップのテスト"""
    # エントリーを作成
    entry = Entry(
        user_id=test_user.id,
        title="Test Title",
        content="Test Content"
    )
    db.session.add(entry)
    db.session.commit()

    # DiaryItemを追加
    item1 = DiaryItem(
        entry_id=entry.id,
        item_name="Item 1",
        item_content="Content 1"
    )
    item2 = DiaryItem(
        entry_id=entry.id,
        item_name="Item 2",
        item_content="Content 2"
    )
    db.session.add(item1)
    db.session.add(item2)
    db.session.commit()

    # リレーションシップを確認
    assert entry.user == test_user
    assert len(entry.items) == 2
    assert entry.items[0].item_name == "Item 1"
    assert entry.items[1].item_name == "Item 2"

    # カスケード削除を確認
    db.session.delete(entry)
    db.session.commit()

    # DiaryItemも削除されていることを確認
    items = DiaryItem.query.all()
    assert len(items) == 0
