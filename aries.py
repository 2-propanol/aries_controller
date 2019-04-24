#!/usr/bin/env python3
# -*- coding: utf-8 -*

"""
    ARIES 3軸ステージをPythonで制御する

    Usage: python3 aries.py <ARIESのIPアドレス> <operation> <args>...

    <ARIESのIPアドレス>
        defaultでは 192.168.1.20が使用される

    <operation>

"""

import argparse
from telnetlib import Telnet
# import time


class Aries:
    """
    ARIES 3軸ステージを制御するクラス

    Parameters
    ----------
    is_connected : bool
        telnetが生きていればTrue、死んでいればFalseを返す。

    Attributes
    ----------
    `host` : str
        ARIESのIPアドレス。デフォルトは "192.168.1.20"。
    `port` : int
        ARIESの接続に使うポート番号。デフォルトは 12321。
    """

    _EOL = b"\r\n"
    is_connected = False

    def __init__(self, host="192.168.1.20", port=12321):
        """
        コンストラクタ。telnetへ接続開始。

        10秒経って接続されなかったらタイムアウトする。
        同期処理のため、接続されるか10秒経つまで待機する。
        """

        try:
            self.tn = Telnet(host, port, 10)
        except Exception as err:
            # ホストが見つからなかったときやタイムアウトが起こったときを想定
            # 他のエラーも握り潰しているためリファクタリングの余地あり
            # （ConnectionRefusedError は観測済み）
            print(">>> ", err)
        else:
            self.is_connected = True

    def __del__(self):
        """
        デストラクタ。telnetから切断。

        telnetプロセスがpython終了後も残るのを防ぐため。
        `del aries`のように明示的に呼び出す必要はない。
        """

        try:
            self.tn.close()
            self.is_connected = False
        except AttributeError:
            # そもそもtelnetに接続されなかったときの例外
            pass

    def raw_command(self, cmd, timeout=300):
        """
        "RPS1/4/90000/1"のような従来のコマンドをそのまま使用する。
        同期処理のため返答があるまで待機する。

        Parameters
        ----------
        cmd : str
            対象の果物のマスタID。
        timeout : int
            返答を待機する最大秒数。デフォルトは300秒。

        Returns
        -------
        stdout : str
            コマンド実行結果。

        `WAP`(アプリケーション接続数設定 書換), `TRS`(トリガ信号出力選択)などの
        このクラスで実装されていないコマンドも実行可能。
        """

        self.tn.write(cmd.encode())
        self.tn.write(self._EOL)

        # 改行されるまで待機して、得られた内容を返す
        return self.tn.read_until(b"\r\n", timeout).decode()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", type=str,
                        help="transfering command to ARIES")
    parser.add_argument("--host", type=str,
                        help="ARIES's IP address. default is 192.168.1.20")
    parser.add_argument("--port", type=int,
                        help="ARIES's port. default is 12321")

    args = parser.parse_args()
    if args.host is None:
        args.host = "192.168.1.20"
    if args.port is None:
        args.port = 12321

    # aries = Aries("192.168.1.20", 12321)
    aries = Aries(host=args.host, port=args.port)

    # 接続されているかを is_connected で調べる
    if aries.is_connected:
        print("connected")
    else:
        print("connection failed")
        return 1

    result = aries.raw_command(args.command)
    print(result)

    return 0


if __name__ == '__main__':
    main()
