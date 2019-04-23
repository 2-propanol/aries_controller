#!/usr/bin/env python
# -*- coding: utf-8 -*

"""
    ARIES 3軸ステージをPythonで制御する

    Usage: python3 aries.py <ARIESのIPアドレス> <operation> <args>...

    <ARIESのIPアドレス>
        defaultでは 192.168.1.20が使用される

    <operation>

"""

import sys
from telnetlib import Telnet
# import time


class Aries:
    """
    ARIES 3軸ステージを制御するクラス

    Attributes
    ----------
    `host` : str
        ARIESのIPアドレス。デフォルトは "192.168.1.20"。
    `port` : int
        ARIESの接続に使うポート番号。デフォルトは 12321。
    """

    def __init__(self, host="192.168.1.20", port=12321):
        """
        コンストラクタ。telnetへ接続開始。
        """

        self.tn = Telnet(host, port)

    def __del__(self):
        """
        デストラクタ。telnetから切断。

        telnetプロセスがpython終了後も残るのを防ぐため。
        明示的に呼び出す必要はない。
        """

        self.tn.close()


def main():
    print("tn opening")

    aries = Aries()

    print("tn opened")

    # tn.write(b"RPS1/2/9000/1\r\n")
    # tn.write(b"ORG3/3/1\r\n")

    print("tn wrote")

    # print(tn.read_all().decode('ascii'))

    print("tn closing")
    del aries
    print("tn closed")
    return 0


if __name__ == '__main__':
    args = sys.argv

    print(args)
    print("第1引数：" + args[1])

    main()
