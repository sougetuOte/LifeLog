from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import datetime
import re
import functools
from database import db, init_db
from models import User, Entry, DiaryItem, create_initial_data
from sqlalchemy import select, desc

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # 本番環境では安全な値に変更してください

# データベース初期化
init_db(app)

MAX_LOGIN_ATTEMPTS = 3  # ログイン試行回数を3回に変更

# ログイン必須デコレータ
def login_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'ログインが必要です'}), 401
        return f(*args, **kwargs)
    return decorated_function

# 管理者必須デコレータ
def admin_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or not session.get('is_admin'):
            return jsonify({'error': '管理者権限が必要です'}), 403
        return f(*args, **kwargs)
    return decorated_function

# ルート
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')

@app.route('/settings', methods=['GET'])
@login_required
def settings():
    return render_template('settings.html')

@app.route('/admin', methods=['GET'])
@admin_required
def admin():
    return render_template('admin.html')

@app.route('/api/login', methods=['POST'])
def api_login():
    userid = request.json.get('userid')
    password = request.json.get('password')
    
    if not userid or not password:
        return jsonify({'error': 'ユーザーIDとパスワードを入力してください'}), 400

    stmt = select(User).filter_by(userid=userid, is_visible=True)
    user = db.session.execute(stmt).scalar_one_or_none()

    if not user:
        return jsonify({'error': 'ユーザーIDまたはパスワードが正しくありません'}), 401

    if user.is_locked:
        return jsonify({'error': 'アカウントがロックされています。管理者に連絡してください'}), 403

    if user.check_password(password):
        # ログイン成功時の処理
        user.login_attempts = 0
        user.last_login_attempt = None
        db.session.commit()
        
        session['user_id'] = user.id
        session['is_admin'] = user.is_admin
        session['name'] = user.name
        session['userid'] = user.userid
        return jsonify({'message': 'ログインしました'})
    else:
        # ログイン失敗時の処理
        user.login_attempts += 1
        user.last_login_attempt = datetime.datetime.now()
        if user.login_attempts >= MAX_LOGIN_ATTEMPTS:
            user.is_locked = True
        db.session.commit()
        
        attempts_left = MAX_LOGIN_ATTEMPTS - user.login_attempts
        if attempts_left > 0:
            return jsonify({'error': f'パスワードが正しくありません。あと{attempts_left}回間違えるとロックされます'}), 401
        else:
            return jsonify({'error': 'アカウントがロックされました。管理者に連絡してください'}), 403

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'ログアウトしました'})

@app.route('/api/user/settings', methods=['PUT'])
@login_required
def update_user_settings():
    name = request.json.get('name')
    current_password = request.json.get('currentPassword')
    new_password = request.json.get('newPassword')
    
    stmt = select(User).filter_by(id=session['user_id'], is_visible=True)
    user = db.session.execute(stmt).scalar_one_or_none()
    
    if not user:
        return jsonify({'error': 'ユーザーが見つかりません'}), 404
    
    # パスワード変更がある場合
    if current_password and new_password:
        if not user.check_password(current_password):
            return jsonify({'error': '現在のパスワードが正しくありません'}), 400
            
        user.password = new_password  # TODO: パスワードのハッシュ化
        user.name = name
    else:
        # 名前のみ更新
        user.name = name
    
    db.session.commit()
    session['name'] = name
    return jsonify({'message': '設定を更新しました'})

@app.route('/api/user/deactivate', methods=['POST'])
@login_required
def deactivate_account():
    password = request.json.get('password')
    if not password:
        return jsonify({'error': 'パスワードを入力してください'}), 400

    stmt = select(User).filter_by(id=session['user_id'], is_visible=True)
    user = db.session.execute(stmt).scalar_one_or_none()

    if not user:
        return jsonify({'error': 'ユーザーが見つかりません'}), 404

    if not user.check_password(password):
        return jsonify({'error': 'パスワードが正しくありません'}), 400

    # 管理者は退会できない
    if user.is_admin:
        return jsonify({'error': '管理者アカウントは退会できません'}), 403

    # ユーザーを不可視に設定
    user.is_visible = False
    db.session.commit()
    session.clear()
    return jsonify({'message': '退会処理が完了しました'})

@app.route('/api/admin/users', methods=['GET'])
@admin_required
def get_users():
    stmt = select(User).filter(User.userid != session['userid']).order_by(User.userid)
    users = db.session.execute(stmt).scalars().all()
    
    return jsonify([{
        'id': user.id,
        'userid': user.userid,
        'name': user.name,
        'is_admin': user.is_admin,
        'is_locked': user.is_locked,
        'is_visible': user.is_visible,
        'login_attempts': user.login_attempts,
        'last_login_attempt': user.last_login_attempt.isoformat() if user.last_login_attempt else None,
        'entries_count': db.session.query(Entry).filter_by(user_id=user.id).count()
    } for user in users])

@app.route('/api/admin/users/<int:user_id>/unlock', methods=['POST'])
@admin_required
def unlock_user(user_id):
    user = db.session.get_or_404(User, user_id)
    user.is_locked = False
    user.login_attempts = 0
    user.last_login_attempt = None
    db.session.commit()
    return jsonify({'message': 'アカウントのロックを解除しました'})

@app.route('/api/admin/users/<int:user_id>/toggle-admin', methods=['POST'])
@admin_required
def toggle_admin(user_id):
    user = db.session.get_or_404(User, user_id)
    user.is_admin = not user.is_admin
    db.session.commit()
    return jsonify({'message': '管理者権限を更新しました'})

@app.route('/api/admin/users/<int:user_id>/toggle-visibility', methods=['POST'])
@admin_required
def toggle_visibility(user_id):
    user = db.session.get_or_404(User, user_id)
    
    # 管理者は削除できない
    if user.is_admin:
        return jsonify({'error': '管理者アカウントは削除できません'}), 403
        
    user.is_visible = not user.is_visible
    db.session.commit()
    
    action = '復元' if user.is_visible else '削除'
    return jsonify({'message': f'ユーザーを{action}しました'})

@app.route('/entries', methods=['GET'])
def get_entries():
    if 'user_id' in session and session.get('is_admin'):
        # 管理者は全ての投稿を表示（退会ユーザーの投稿も含む）
        stmt = select(Entry).join(User).order_by(
            desc(Entry.updated_at if Entry.updated_at is not None else Entry.created_at)
        )
    else:
        # 未ログインユーザーまたは一般ユーザーは可視状態のユーザーの投稿のみ表示
        stmt = select(Entry).join(User).filter(User.is_visible == True).order_by(
            desc(Entry.updated_at if Entry.updated_at is not None else Entry.created_at)
        )
    
    entries = db.session.execute(stmt).scalars().all()

    return jsonify([{
        'id': entry.id,
        'title': entry.title,
        'content': entry.content,
        'notes': entry.notes,
        'items': [{
            'item_name': item.item_name,
            'item_content': item.item_content
        } for item in entry.items],
        'created_at': entry.created_at.isoformat() if entry.created_at else None,
        'updated_at': entry.updated_at.isoformat() if entry.updated_at else None,
        'author_name': entry.user.name,
        'author_userid': entry.user.userid,
        'is_visible': entry.user.is_visible,
        'user_id': entry.user_id,
        'can_edit': 'user_id' in session and (
            session.get('is_admin') or (entry.user_id == session['user_id'] and entry.user.is_visible)
        )
    } for entry in entries])

@app.route('/entries', methods=['POST'])
@login_required
def add_entry():
    title = request.json.get('title')
    content = request.json.get('content')
    notes = request.json.get('notes', '')
    items = request.json.get('items', [])
    
    if not title:
        return jsonify({'error': 'タイトルが空です'}), 400
    if not content:
        return jsonify({'error': '内容が空です'}), 400
    
    user = db.session.get(User, session['user_id'])
    if not user or not user.is_visible:
        return jsonify({'error': 'アカウントが無効です'}), 403

    try:
        # エントリーを作成
        entry = Entry(
            user_id=session['user_id'],
            title=title,
            content=content,
            notes=notes,
            created_at=datetime.datetime.now()
        )
        db.session.add(entry)
        db.session.flush()  # IDを生成するためにflush

        # 活動項目を追加
        for item in items:
            diary_item = DiaryItem(
                entry_id=entry.id,
                item_name=item['item_name'],
                item_content=item['item_content'],
                created_at=datetime.datetime.now()
            )
            db.session.add(diary_item)

        db.session.commit()
        return jsonify({'message': '投稿が完了しました'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '投稿に失敗しました'}), 500

@app.route('/entries/<int:entry_id>', methods=['PUT'])
@login_required
def update_entry(entry_id):
    stmt = select(Entry).join(User).filter(Entry.id == entry_id)
    entry = db.session.execute(stmt).scalar_one_or_none()
    
    if not entry:
        return jsonify({'error': '投稿が見つかりません'}), 404
    
    # 管理者以外の場合、退会済みユーザーは編集不可
    if not session.get('is_admin') and (
        entry.user_id != session['user_id'] or not entry.user.is_visible
    ):
        return jsonify({'error': '編集権限がありません'}), 403

    title = request.json.get('title')
    content = request.json.get('content')
    notes = request.json.get('notes', '')
    items = request.json.get('items', [])
    
    if not title:
        return jsonify({'error': 'タイトルが空です'}), 400
    if not content:
        return jsonify({'error': '内容が空です'}), 400
    
    try:
        # エントリーを更新
        entry.title = title
        entry.content = content
        entry.notes = notes
        entry.updated_at = datetime.datetime.now()

        # 既存の活動項目を削除
        stmt = select(DiaryItem).filter_by(entry_id=entry.id)
        existing_items = db.session.execute(stmt).scalars().all()
        for item in existing_items:
            db.session.delete(item)

        # 新しい活動項目を追加
        for item in items:
            diary_item = DiaryItem(
                entry_id=entry.id,
                item_name=item['item_name'],
                item_content=item['item_content'],
                created_at=datetime.datetime.now()
            )
            db.session.add(diary_item)

        db.session.commit()
        return jsonify({'message': '更新が完了しました'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '更新に失敗しました'}), 500

@app.route('/entries/<int:entry_id>', methods=['DELETE'])
@login_required
def delete_entry(entry_id):
    stmt = select(Entry).join(User).filter(Entry.id == entry_id)
    entry = db.session.execute(stmt).scalar_one_or_none()
    
    if not entry:
        return jsonify({'error': '投稿が見つかりません'}), 404
    
    # 管理者以外の場合、退会済みユーザーは削除不可
    if not session.get('is_admin') and (
        entry.user_id != session['user_id'] or not entry.user.is_visible
    ):
        return jsonify({'error': '削除権限がありません'}), 403

    try:
        db.session.delete(entry)
        db.session.commit()
        return jsonify({'message': '削除が完了しました'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '削除に失敗しました'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
