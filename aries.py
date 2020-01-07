"""ARIES 3軸ステージをPythonで制御する

    Usage: python3 aries.py --host <HOST> --port <PROT> <operation>

    <HOST>
        ARIESのIPアドレス。省略すると 192.168.1.20 が使用される

    <PORT>
        ARIESのポート番号。省略すると 12321 が使用される

    <operation>
        ARIESに送信するコマンド。RPS1/4/90000/1 など。
"""

import time
from telnetlib import Telnet
from socket import timeout as socket_timeout


class Aries:
    """ARIES 3軸ステージを制御するクラス

    Params:
        is_connected (bool): telnetが生きていればTrue、死んでいればFalseを返す。
        is_stopped (bool): 3軸全てが停止していればTrue。Trueを代入すると緊急停止
        speed (int): 移動速度(1〜9)。int以外が代入された場合、型変換を試みる。
        x (int): ARIESの1軸パルス値と連動。-45,000 〜 +45,000。
        y (int): ARIESの2軸パルス値と連動。0 〜 +90,000。
        z (int): ARIESの3軸パルス値と連動。180,000で一周。-360,000 〜 +360,000。
        x_by_degree (float): xを角度で読み書き。分解能は0.002度。
        y_by_degree (float): yを角度で読み書き。分解能は0.001度。
        z_by_degree (float): zを角度で読み書き。分解能は0.002度。

    Attributes:
        host (str): ARIESのIPアドレス。デフォルトは "192.168.1.20"。
        port (int): ARIESの接続に使うポート番号。デフォルトは 12321。
    """

    is_connected = False
    _speed = 4

    # 駆動要求を発行した後の待機時間
    INTERVAL_TIME = 0.1

    def __init__(self, host="192.168.1.20", port=12321, timeout=10):
        """コンストラクタ。telnetへ接続開始。

        接続されるかタイムアウトするまで待機する。
        """

        try:
            self.tn = Telnet(host, port, timeout)
        except (ConnectionRefusedError, socket_timeout) as err:
            print("ARIES: error: ", err)
        else:
            self.is_connected = True

    def __del__(self):
        """デストラクタ。telnetから切断。

        telnetプロセスがpython終了後も残るのを防ぐため。
        `del aries`のように明示的に呼び出す必要はない。
        """

        try:
            self.tn.close()
            self.is_connected = False
        except AttributeError:
            # そもそもtelnetに接続されなかったときの例外
            pass

    def _clip(self, orig, min, max, str=""):
        """origをintに変換し、minとmax内に収める。

        プライベートメソッド想定。
        変換できなかった場合は例外を発生させる。

        Args:
            orig (any): clip対象の値。
            min (int): 最小値。
            max (int): 最大値。
            str (str): エラーメッセージに使う文字列。

        Returns:
            int: 変換済みの値。
        """
        try:
            orig = int(orig)
        except ValueError:
            raise ValueError(f"ARIES: error: '{orig}' is not int. in {str}")
        else:
            if orig > max:
                print(f"ARIES: warn: {str} is limited to {max}.")
                return max
            elif orig < min:
                print(f"ARIES: warn: {str} is limited to {min}.")
                return min
            else:
                return orig

    def raw_command(self, cmd, timeout=300):
        """"RPS1/4/90000/1"のような従来のコマンドをそのまま使用する。

        返答があるまで待機する。

        Args:
            cmd (str): telnetに送信するコマンド。
            timeout (int): 返答を待機する最大秒数。デフォルトは300秒。

        Returns:
            str: 生のコマンド実行結果。
        """

        self.tn.write(cmd.encode())
        self.tn.write(b"\r\n")

        # 改行されるまで待機して、得られた内容を返す
        return self.tn.read_until(b"\r\n", timeout).decode()

    def reset(self):
        """原点近接センサ・エッジを用いてステージを厳密に原点へ復帰させる。

        電源投入直後や長時間駆動させた後に実行することで、
        ステージ位置の信頼性を向上できる。
        """

        self.raw_command(f"ORG1/{self._speed}/1")
        self.raw_command(f"ORG2/{self._speed}/1")
        self.raw_command(f"ORG3/{self._speed}/1")

    def sleep_until_stop(self):
        """ステージが停止状態になるまでsleepする。
        """

        while not self.is_stopped:
            time.sleep(0.5)

    @property
    def x(self):
        return int(self.raw_command("RDP1").split()[2])

    @property
    def y(self):
        return int(self.raw_command("RDP2").split()[2])

    @property
    def z(self):
        return int(self.raw_command("RDP3").split()[2])

    @x.setter
    def x(self, x):
        self.raw_command(
            f"APS1/{self._speed}/{self._clip(x, -45000, 45000, 'x')}/1")
        time.sleep(self.INTERVAL_TIME)

    @y.setter
    def y(self, y):
        self.raw_command(
            f"APS2/{self._speed}/{self._clip(y, 0, 90000, 'y')}/1")
        time.sleep(self.INTERVAL_TIME)

    @z.setter
    def z(self, z):
        self.raw_command(
            f"APS3/{self._speed}/{self._clip(z, -134217728, 134217727, 'z')}/1")
        time.sleep(self.INTERVAL_TIME)

    @property
    def x_by_degree(self):
        return self.x / 500

    @property
    def y_by_degree(self):
        return self.y / 1000

    @property
    def z_by_degree(self):
        return self.z / 500

    @x_by_degree.setter
    def x_by_degree(self, x_by_degree):
        self.x = x_by_degree * 500

    @y_by_degree.setter
    def y_by_degree(self, y_by_degree):
        self.y = y_by_degree * 1000

    @z_by_degree.setter
    def z_by_degree(self, z_by_degree):
        self.z = z_by_degree * 500

    @property
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, speed):
        self._speed = self._clip(speed, 0, 9, "speed")

    @property
    def is_stopped(self):
        # 3軸全てが停止状態であれば True
        return self.raw_command("STR1").split()[2] == "0" \
            and self.raw_command("STR2").split()[2] == "0" \
            and self.raw_command("STR3").split()[2] == "0"

    @is_stopped.setter
    def is_stopped(self, _is_stopped):
        if _is_stopped:
            # 3軸全てを緊急停止させる
            self.raw_command("STP1/0")
            self.raw_command("STP2/0")
            self.raw_command("STP3/0")
        else:
            # 非常停止信号のソフトウェアロックを解除する
            self.raw_command("REM")


def main():
    """コマンドラインツールとして使用するときの処理"""
    import argparse
    import sys

    parser = argparse.ArgumentParser()
    parser.add_argument("command", type=str,
                        help="transfering command to ARIES")
    parser.add_argument("--host", type=str, default="192.168.1.20",
                        help="ARIES's IP address. default is 192.168.1.20")
    parser.add_argument("--port", type=int, default=12321,
                        help="ARIES's port. default is 12321")
    args = parser.parse_args()

    # ARIESへの接続を試みる
    print(f"Trying {args.host}:{args.port}.")
    aries = Aries(host=args.host, port=args.port)

    # 接続されているかを is_connected で調べる
    if aries.is_connected:
        print(f"connected to {args.host}:{args.port}.")
    else:
        print("connection failed.")
        sys.exit(1)

    # コマンドの実行と結果の表示
    result = aries.raw_command(args.command)
    print(result)

    # 明示的な切断要求(デストラクタがあるので書かなくても良い)
    del aries
    print("connection closed.")
    sys.exit(0)


if __name__ == '__main__':
    main()
