# テストデータ生成CLI仕様書

## 1. 概要

テストデータの生成、管理を行う対話式CLIツール。
データの生成、削除、挿入の各操作を独立して実行可能。

## 2. コマンド体系

### 2.1 基本構造

```bash
python manage_test_data.py [command] [options]
```

注：コマンドを指定しない場合、自動的に対話モードが起動します。

### 2.2 コマンド一覧

1. generate (gen)
   - テストデータの生成
   - 生成したデータはJSONファイルとして保存

2. clear (clr)
   - DB内の既存データを削除
   - 削除対象の指定が可能

3. insert (ins)
   - 生成済みのテストデータをDBに挿入
   - JSONファイルから読み込み

4. interactive (i)
   - 対話モードを起動
   - 各種操作をステップバイステップで実行

## 3. コマンド詳細

### 3.1 generate

```bash
python manage_test_data.py generate [options]
```

オプション：
- --start YYYY/MM/DD : 開始日（必須）
- --end YYYY/MM/DD : 終了日（必須）
- --rate N : データ生成率（1-100%、デフォルト100%）
- --items-per-entry M : 活動項目数（デフォルト0-3）
- --output FILE : 出力JSONファイル名（デフォルト: test_data_YYYYMMDD_HHMMSS.json）

### 3.2 clear

```bash
python manage_test_data.py clear [options]
```

オプション：
- --all : 全データを削除
- --start YYYY/MM/DD : 削除開始日
- --end YYYY/MM/DD : 削除終了日
- --user USER_ID : 特定ユーザーのデータのみ削除
- --confirm : 削除確認をスキップ

注：データ削除時は自動的にバックアップが作成されます（設定でOFF可能）。
バックアップは `backups` ディレクトリに保存され、タイムスタンプ付きで管理されます。

### 3.3 insert

```bash
python manage_test_data.py insert [options]
```

オプション：
- --file FILE : 挿入するJSONファイル（必須）
- --dry-run : 実際の挿入を行わず、検証のみ実行
- --skip-validation : バリデーションをスキップ

### 3.4 interactive

```bash
python manage_test_data.py interactive
```

対話モードでは以下の操作をメニュー形式で提供：

1. データ生成
   - 日付範囲の入力
   - 生成率の設定
   - 活動項目数の設定
   - 出力ファイル名の指定

2. データ削除
   - 削除範囲の選択
   - 対象ユーザーの選択
   - 確認プロンプト

3. データ挿入
   - JSONファイルの選択
   - バリデーション実行
   - 挿入前の確認

4. 終了

## 4. データ生成ルール

### 4.1 基本ルール
- ユーザー：admin, tetsu, gentoから選択
- 1ユーザー1日1エントリーまで
- 最大エントリー数 = 日数 × 3（ユーザー数）

### 4.2 生成データの内容
- タイトル：テンプレートベースでランダム生成
- 内容：テンプレートベースでランダム生成
- メモ：天気、気分などのパターンからランダム選択
- 活動項目：設定された範囲内でランダム生成

## 5. バリデーション

### 5.1 日付のバリデーション
- 形式：YYYY/MM/DD
- 開始日 ≤ 終了日
- 有効な日付であること

### 5.2 パラメータのバリデーション
- 生成率：1-100%の整数
- 活動項目数：0以上の整数

### 5.3 データ整合性チェック
- ユーザーIDの存在確認
- 日付の重複チェック
- 必須フィールドの存在確認

## 6. エラー処理

### 6.1 エラーメッセージ
- 日本語での明確なエラー表示
- エラーの原因と対処方法を提示

### 6.2 エラーログ
- エラー発生時のログ記録
- 詳細なスタックトレース（開発モードのみ）

## 7. 出力形式

### 7.1 JSONファイル構造
```json
{
  "metadata": {
    "generated_at": "YYYY/MM/DD HH:MM:SS",
    "parameters": {
      "start_date": "YYYY/MM/DD",
      "end_date": "YYYY/MM/DD",
      "rate": N,
      "items_per_entry": M
    }
  },
  "entries": [
    {
      "user_id": "string",
      "date": "YYYY/MM/DD",
      "title": "string",
      "content": "string",
      "notes": "string",
      "items": [
        {
          "item_name": "string",
          "item_content": "string"
        }
      ]
    }
  ]
}
```

### 7.2 ログ出力
- 操作の実行状況
- 生成データの統計情報
- エラーや警告メッセージ

## 8. 設定ファイル

### 8.1 config.yaml
```yaml
# テンプレート設定
templates:
  titles:
    - "日記 - {date}"
    - "{weather}の一日"
  contents:
    - "今日は{activity}をした。"
    - "{feeling}一日だった。"
  notes:
    weather:
      - "晴れ"
      - "曇り"
      - "雨"
    feeling:
      - "楽しい"
      - "充実した"
      - "疲れた"
  items:
    - "運動"
    - "読書"
    - "勉強"

# 生成設定
generation:
  default_rate: 100
  default_items_per_entry: 3
  output_dir: "test_data"

# データベース設定
database:
  backup_before_clear: true
  backup_dir: "backups"
```

## 9. 使用例

### 9.1 対話モードでの使用

```bash
$ python manage_test_data.py interactive

テストデータ管理ツール

1. データ生成
2. データ削除
3. データ挿入
4. 終了

選択してください (1-4): 1

=== データ生成 ===
開始日 (YYYY/MM/DD): 2024/01/01
終了日 (YYYY/MM/DD): 2024/01/31
生成率 (1-100%) [100]: 80
活動項目数 (0-10) [3]: 2
出力ファイル名 [test_data_20240101_20240131.json]: 

テストデータを生成しました: test_data_20240101_20240131.json

1. データ生成
2. データ削除
3. データ挿入
4. 終了

選択してください (1-4): 2

=== データ削除 ===
削除範囲を選択してください:
1. 全データ
2. 日付範囲指定
3. ユーザー指定
4. 戻る

選択してください (1-4): 2

開始日 (YYYY/MM/DD): 2024/01/01
終了日 (YYYY/MM/DD): 2024/01/31

以下のデータを削除します:
期間: 2024/01/01 - 2024/01/31
エントリー数: 45

続行しますか？ (y/N): y

45件のデータを削除しました

1. データ生成
2. データ削除
3. データ挿入
4. 終了

選択してください (1-4): 3

=== データ挿入 ===
JSONファイル: test_data_20240101_20240131.json

バリデーションを実行中...
OK

以下のデータを挿入します:
期間: 2024/01/01 - 2024/01/31
エントリー数: 45

続行しますか？ (y/N): y

45件のエントリーを挿入しました

1. データ生成
2. データ削除
3. データ挿入
4. 終了

選択してください (1-4): 4

終了します。
```

### 9.2 コマンドラインでの使用

```bash
# データ生成
$ python manage_test_data.py generate --start 2024/01/01 --end 2024/01/31 --rate 80 --items-per-entry 2

# データ削除
$ python manage_test_data.py clear --start 2024/01/01 --end 2024/01/31 --confirm

# データ挿入
$ python manage_test_data.py insert --file test_data_20240101_20240131.json
