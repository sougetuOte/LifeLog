# LifeLog

## 概要
LifeLogは、ユーザーが日々の活動を記録・管理できる日記管理システムです。

## 機能
- ユーザー認証と管理
- 日記エントリの作成と管理
- 多言語対応（英語/日本語）

## インストール
```bash
# conda環境の作成
conda create -n lifelog python=3.11.10
conda activate lifelog

# 依存関係のインストール
pip install -r requirements.txt

# データベースの初期化
python create_data.py
```

## 使用方法
```bash
# 開発サーバーの起動
python app.py
```

Webブラウザで http://localhost:5000 にアクセスしてください。

## 更新履歴
- 2024/12/01: 0.01公開
- 2024/12/08: モデル構造の改善とテストの追加
- 2024/12/09: マイグレーション機能の追加
- 2024/12/10: 開発環境をcondaベースに変更
