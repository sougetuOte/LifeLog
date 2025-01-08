#!/usr/bin/env python
"""
テストデータ管理ツール

使用方法:
    $ python manage_test_data.py [command] [options]

コマンド:
    generate (gen)  テストデータの生成
    clear (clr)     DBデータの削除
    insert (ins)    テストデータの挿入
    interactive (i) 対話モードを起動

オプションの詳細は各コマンドの --help を参照してください。
"""

from manage_test_data.cli import main

if __name__ == '__main__':
    main()
