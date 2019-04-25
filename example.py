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

    # コマンドの実行など
    aries.reset_position()

    return 0


if __name__ == '__main__':
    main()
