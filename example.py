#!/usr/bin/env python3
# -*- coding: utf-8 -*

"""
    aries.pyのモジュールとしての使用例
"""

from aries import Aries
import time


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

    # コマンドの実行
    aries.reset()  # 初期位置に戻す
    aries.wait_until_stop()  # 停止するまで待機する

    for i in range(3):
        aries.x = -45000
        aries.y += 30000
        for j in range(9):
            time.sleep(1)
            aries.x += 10000
            aries.wait_until_stop()
            print(f"shot {aries.x},{aries.y}")
            time.sleep(1)

    return 0


if __name__ == '__main__':
    main()
