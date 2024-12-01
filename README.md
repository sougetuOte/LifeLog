# LifeLogについて

シンプルな日記投稿・管理システムです。ユーザー認証機能を備え、一般ユーザーと管理者の権限分けがある日記アプリケーションです。

## 主な機能

- ユーザー管理（登録、認証、権限制御）
- 日記の投稿・編集・削除
- 管理者機能（ユーザー管理、コンテンツ管理）
- シンプルで使いやすいインターフェース

## 技術スタック

- Python 3.11.9
- Flask 3.1.0
- SQLite3
- HTML/CSS/JavaScript

## セットアップ方法

1. Python環境の準備
```bash
pyenv install 3.11.9
pyenv local 3.11.9
python -m venv venv
source venv/bin/activate
```

2. 依存パッケージのインストール
```bash
pip install -r requirements.txt
```

3. データベースの初期化と起動
```bash
python -c "from app import init_db; init_db()"
python app.py
```

アプリケーションの起動後、ブラウザで http://127.0.0.1:5000 にアクセスしてください。

## 初期アカウント

管理者アカウント：
- ユーザーID: admin
- パスワード: Admin3210

## 制限事項

現在の開発版では以下の制限があります：
- ファイルアップロード機能なし
- ページネーション機能なし
- パスワードリセット機能なし
- 退会処理の取り消し機能なし

## ライセンス
- [MIT License](LICENSE)

## 詳細仕様

アプリケーションの詳細な仕様については [仕様書](docs/specification.md) を参照してください。