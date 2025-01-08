#!/usr/bin/env python
import sys
from .manager import TestDataManager

def main():
    try:
        manager = TestDataManager()

        # コマンドライン引数がない場合は対話モードを起動
        if len(sys.argv) == 1:
            manager.interactive()
            return

        # コマンドライン引数の処理は manager.py の main() に委譲
        from .manager import main as manager_main
        manager_main()

    except Exception as e:
        print(f'エラーが発生しました: {e}', file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
