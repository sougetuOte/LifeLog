import os
import datetime
import re

"""
除外するディレクトリとファイル：
- __pycache__ ディレクトリ
- .git ディレクトリ
- tests/instance ディレクトリ（テスト用データベース）
- migrations/versions （データベースマイグレーションファイル）
- node_modules （もし存在する場合）
- .pyc ファイル
- .db, .sqlite3 ファイル
- .log ファイル
- .env ファイル
- package-lock.json （依存関係のロックファイル）
- lifelog_all_*.md （過去のマージファイル）
- .pytest_cache （Pytestのキャッシュディレクトリ）
- docs/diagrams.md （英語の設計図ドキュメント）
- docs/specification.md （英語の仕様ドキュメント）
- README.md （プロジェクト説明ドキュメント）
"""

def should_exclude(path):
    # 除外するディレクトリやファイル
    exclude_patterns = [
        r'__pycache__',
        r'\.git',
        r'tests/instance',
        r'node_modules',
        r'\.pyc$',
        r'\.db$',
        r'\.sqlite3$',
        r'\.log$',
        r'\.env$',
        r'\.coveragerc$',
        r'package-lock\.json$',
        r'lifelog_all_\d{8}(_\d+)?\.md$',  # マージ出力ファイルのパターン
        r'\.pytest_cache',  # Pytestのキャッシュディレクトリ
        r'docs/diagrams\.md$',  # 英語の設計図ドキュメント
        r'docs/specification\.md$',  # 英語の仕様ドキュメント
        r'README\.md$'  # プロジェクト説明ドキュメント
    ]
    
    return any(re.search(pattern, path) for pattern in exclude_patterns)

def get_output_filename(base_dir):
    base_name = os.path.join(base_dir, f"lifelog_all_{datetime.datetime.now().strftime('%Y%m%d')}.md")
    if not os.path.exists(base_name):
        return base_name
    
    counter = 1
    while True:
        new_name = os.path.join(base_dir, f"lifelog_all_{datetime.datetime.now().strftime('%Y%m%d')}_{counter}.md")
        if not os.path.exists(new_name):
            return new_name
        counter += 1

def merge_files():
    # 現在のスクリプトが存在するディレクトリを取得
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_filename = get_output_filename(base_dir)
    
    with open(output_filename, 'w', encoding='utf-8') as outfile:
        for root, dirs, files in os.walk(base_dir):
            # 除外するディレクトリをスキップ
            dirs[:] = [d for d in dirs if not should_exclude(os.path.join(root, d))]
            
            for file in sorted(files):
                filepath = os.path.join(root, file)
                
                # 出力ファイル自体をスキップ
                if os.path.samefile(filepath, output_filename):
                    continue
                
                # 除外するファイルをスキップ
                if should_exclude(filepath):
                    continue
                
                # バイナリファイルや特定の拡張子をスキップ
                if not any(file.endswith(ext) for ext in ['.py', '.md', '.txt', '.html', '.css', '.js', '.json', '.ini', '.sql']):
                    continue
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as infile:
                        # ベースディレクトリからの相対パスを取得
                        relative_path = os.path.relpath(filepath, base_dir)
                        # パスをエスケープして表示
                        escaped_path = f"[* '{relative_path.replace(os.sep, '/')}']"
                        outfile.write(f"\n\n## {escaped_path}\n\n")
                        
                        # ファイルの内容を書き込む
                        content = infile.read()
                        outfile.write(content)
                except Exception as e:
                    print(f"Error processing {filepath}: {str(e)}")
    
    return output_filename

if __name__ == '__main__':
    output_file = merge_files()
    print(f"マージが完了しました。出力ファイル: {output_file}")
