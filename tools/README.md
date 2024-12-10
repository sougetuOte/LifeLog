# Prompt Manager

プロンプトテンプレートの管理と実行を自動化するツール

## 機能

1. テンプレートの管理
   - YAMLテンプレートの読み込み
   - テンプレートの更新
   - バージョン管理（履歴保存）

2. プロンプトの生成
   - テンプレートベースのプロンプト生成
   - 動的なパラメータ置換
   - フォーマット調整

3. 実行の自動化
   - プロンプトの自動実行
   - 結果の検証
   - エラーハンドリング

## 使用方法

### コマンドライン実行

```bash
# プロンプトテンプレートの実行
python prompt_manager.py prompts security_spec_update

# テストテンプレートの実行
python prompt_manager.py tests unit_test_template
```

### Pythonコードでの使用

```python
from prompt_manager import PromptManager

# マネージャーの初期化
manager = PromptManager()

# プロンプトの生成
prompt = manager.generate_prompt('security_spec_update', 'prompts')

# プロンプトの実行
manager.execute_prompt(prompt)

# テンプレートの更新
updates = {
    'template': '新しいテンプレート内容',
    'notes': '更新された注意事項'
}
manager.update_template('prompts', 'security_spec_update', updates)
```

## ディレクトリ構造

```
docs/
├── prompt_templates.yaml  # プロンプトテンプレート
├── test_templates.yaml   # テストテンプレート
└── history/             # テンプレート更新履歴
    ├── prompt_templates_20240101_120000.yaml
    └── test_templates_20240101_120000.yaml
```

## 注意事項

1. テンプレート更新時は自動的にバックアップが作成されます
2. 履歴は `docs/history` ディレクトリに保存されます
3. エラー発生時は適切なエラーメッセージが表示されます

## 依存パッケージ

```
pyyaml>=6.0.0
```

## インストール

1. 依存パッケージのインストール
```bash
pip install pyyaml
```

2. プロジェクトへの配置
- prompt_manager.py を tools ディレクトリに配置
- テンプレートファイルを docs ディレクトリに配置

## 開発者向け情報

### テンプレートの更新方法

1. テンプレートの構造
```yaml
template_name:
  task: "タスクの説明"
  target_files:
    - "対象ファイル1"
    - "対象ファイル2"
  section: "更新セクション"
  template: |
    テンプレート本文
  notes: |
    注意事項
```

2. 新しいテンプレートの追加
```python
manager = PromptManager()
new_template = {
    'task': '新しいタスク',
    'template': '新しいテンプレート',
    'notes': '注意事項'
}
manager.update_template('prompts', 'new_template_name', new_template)
```

### エラーハンドリング

主なエラーケース：
1. テンプレートファイルが見つからない
2. テンプレート名が存在しない
3. 必須パラメータの欠落
4. YAMLフォーマットエラー

エラー発生時は適切なエラーメッセージと共に例外が発生します。

### 履歴管理

- 更新履歴は自動的に保存されます
- タイムスタンプ付きでバックアップが作成されます
- 履歴からの復元も可能です

## 今後の改善予定

1. テンプレートのバリデーション機能の強化
2. 複数のテンプレートの一括実行
3. 実行結果の自動検証
4. WebUIの追加
