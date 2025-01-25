# LifeLogについて

シンプルな日記投稿・管理システムです。ユーザー認証機能を備え、一般ユーザーと管理者の権限制御がある日記アプリケーションです。

## 重要
- このアプリケーションは開発中のものであり、セキュリティやパフォーマンスの問題がある可能性があります。

## 更新履歴
- 2024/12/01: 0.01公開
- 2024/12/08: モデル構造の改善とテストの追加
- 2024/12/09: マイグレーション機能の追加
- 2024/12/10: テストカバレッジの向上とドキュメントの更新
- 2024/12/10: 環境構築方法の変更（conda対応）とパッケージの更新
- 2025/01/08: ページネーション機能の実装

## 主な機能

- ユーザー管理（登録、認証、権限制御）
- 日記の投稿・編集・削除
- 管理者機能（ユーザー管理、コンテンツ管理）
- シンプルで使いやすいインターフェース
- ページネーション機能（1ページあたり10件表示）

## 技術スタック

- Python 3.11
- Flask 3.1.0
- SQLAlchemy 2.0.36
- Flask-SQLAlchemy 3.1.1
- Alembic 1.14.0
- Flask-WTF 1.2.1
- SQLite3
- HTML/CSS/JavaScript

## セットアップ方法

1. Python環境の準備
```bash
# Minicondaを使用する場合（推奨）
# 1. Minicondaをダウンロードしてインストール: https://docs.conda.io/en/latest/miniconda.html
# 2. 以下のコマンドを実行：
conda create -n lifelog python=3.11
conda activate lifelog
conda install --file requirements.txt

# または、Anacondaを使用する場合
# 1. Anacondaをダウンロードしてインストール: https://www.anaconda.com/download
# 2. 以下のコマンドを実行：
conda create -n lifelog python=3.11
conda activate lifelog
conda install --file requirements.txt
```

注意: Anacondaとminicondaは混在させないでください。どちらか一方を選択して使用してください。

2. データベースのセットアップ
```bash
# マイグレーションの実行
alembic upgrade head

# 初期データの作成
python -c "from models import create_initial_data; create_initial_data()"
```

3. アプリケーションの起動
```bash
python app.py
```

アプリケーションの起動後、ブラウザで http://127.0.0.1:5000 にアクセスしてください。

## テスト実行方法

1. テスト用依存パッケージのインストール
```bash
pip install -r requirements-test.txt
```

2. テストの実行
```bash
pytest
```

テストは以下の範囲をカバーしています：
- ユーザー認証・登録機能（92%のカバレッジ）
- 日記の作成・編集・削除機能（96%のカバレッジ）
- ユーザー管理機能（90%以上のカバレッジ）
- アクセス制御機能
- データベース操作

## 初期アカウント

管理者アカウント：
- ユーザーID: admin
- パスワード: Admin3210

テストユーザー：
- ユーザーID: tetsu
- パスワード: Tetsu3210

- ユーザーID: gento
- パスワード: Gento3210

## 制限事項

現在の開発版では以下の制限があります：
- ファイルアップロード機能なし
- パスワードリセット機能なし
- 退会処理の取り消し機能なし

## ライセンス
- [MIT License](LICENSE)

## 詳細仕様

アプリケーションの詳細な仕様については以下のドキュメントを参照してください：
- [仕様書（日本語）](docs/specification_ja.md)
- [設計図（日本語）](docs/diagrams_ja.md)

## プロジェクト構造

```
/
├── app.py              # メインアプリケーション
├── database.py         # データベース操作
├── models.py           # SQLAlchemyモデル定義（統合版）
├── alembic.ini         # マイグレーション設定
├── models/            # モデル定義
│   ├── __init__.py    # モデルパッケージ初期化
│   ├── base.py        # 基本クラス定義
│   ├── user.py        # ユーザーモデル
│   ├── entry.py       # 日記エントリーモデル
│   ├── diary_item.py  # 日記項目モデル
│   ├── user_manager.py # ユーザー管理機能
│   └── init_data.py   # 初期データ作成
├── static/            # 静的ファイル
│   ├── style.css      # 共通スタイル
│   ├── admin.css      # 管理画面スタイル
│   ├── user.css       # ユーザー設定スタイル
│   ├── main.css       # メインスタイル
│   └── script.js      # クライアントサイドスクリプト
├── templates/         # HTMLテンプレート
│   ├── index.html     # トップページ
│   ├── login.html     # ログインページ
│   ├── register.html  # ユーザー登録ページ
│   ├── settings.html  # ユーザー設定ページ
│   └── admin.html     # 管理者ページ
├── migrations/        # マイグレーションファイル
│   └── versions/      # バージョン管理されたマイグレーション
├── instance/          # インスタンス固有のファイル
│   └── diary.db      # SQLiteデータベース
├── tests/            # テストファイル
│   ├── conftest.py   # テスト共通設定
│   ├── test_user.py  # ユーザーテスト
│   ├── test_entry.py # 日記エントリーテスト
│   └── test_user_manager.py # ユーザー管理テスト
└── docs/             # ドキュメント
    ├── specification.md     # 仕様書（英語）
    ├── specification_ja.md  # 仕様書（日本語）
    ├── diagrams.md         # 設計図（英語）
    └── diagrams_ja.md      # 設計図（日本語）
