#!/usr/bin/env python3
# -*- coding: utf-8 -*

"""
    aries.pyのモジュールとしての使用例
"""

from aries import Aries


def main():
    # ARIESへの接続を試みる
    print("Trying 192.168.1.20:12321.")
    aries = Aries()

    # 接続されているかを is_connected で調べる
    if aries.is_connected:
        print(f"connected to 192.168.1.20:12321.")
    else:
        print("connection failed.")
        return 1

    # コマンドの実行と結果の表示
    result1 = aries.raw_command("ORG1/3/1")
    result2 = aries.raw_command("ORG2/3/1")
    result3 = aries.raw_command("ORG3/3/1")
    print(result1)
    print(result2)
    print(result3)

    print("connection closed.")
    return 0


if __name__ == '__main__':
    main()
