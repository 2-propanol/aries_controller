"""ARIES 3軸ステージをPythonで制御する

Usage: python3 aries.py --host <HOST> --port <PROT> <operation>

<HOST>
    ARIESのIPアドレス。省略すると 192.168.1.20 が使用される

<PORT>
    ARIESのポート番号。省略すると 12321 が使用される

<operation>
    ARIESに送信するコマンド。RPS1/4/90000/1 など。
"""

from socket import timeout as socket_timeout
from telnetlib import Telnet
import time


class Aries:
    """ARIES 3軸ステージを制御するクラス

    Attributes:
        is_stopped (bool): 3軸全てが停止していればTrue。Read-Only。
        speed (int): 3軸全てのステージの移動速度。1〜9。
        x (int): ARIESの1軸パルス値と連動。-45,000 〜 +45,000。
        y (int): ARIESの2軸パルス値と連動。0 〜 +90,000。
        z (int): ARIESの3軸パルス値と連動。180,000で一周。-360,000 〜 +360,000。
        x_by_degree (float): xを角度で読み書き。分解能は0.002度。
        y_by_degree (float): yを角度で読み書き。分解能は0.001度。
        z_by_degree (float): zを角度で読み書き。分解能は0.002度。
    """

    __speed: int = 4

    # 駆動要求を発行した後の待機時間
    INTERVAL_TIME: float = 0.1

    # 各軸の分解能
    PULSE_PER_DEGREE_X: int = 500
    PULSE_PER_DEGREE_Y: int = 1000
    PULSE_PER_DEGREE_Z: int = 500

    def __init__(self, host: str = "192.168.1.20", port: int = 12321,
                 timeout: int = 10) -> None:
        """telnetへ接続要求。

        接続されるかタイムアウトするまで待機する。

        Args:
            host: ARIESのIPアドレス。デフォルトは "192.168.1.20"。
            port: ARIESのポート番号。デフォルトは 12321。
            timeout: 接続試行を打ち切るまでの秒数。デフォルトは 10秒。
        """
        try:
            self.tn = Telnet(host, port, timeout)
        except (ConnectionRefusedError, OSError, socket_timeout) as err:
            raise ConnectionError(f"(ARIES) error: {err}")

    def __del__(self) -> None:
        """telnetから切断。

        telnetプロセスがpython終了後も残るのを防ぐため。
        `del aries`のように明示的に呼び出す必要はない。
        """
        try:
            self.tn.close()
        except AttributeError:
            # そもそもtelnetに接続されなかったときの例外
            pass

    def _clip(self, orig, min: int, max: int) -> int:
        """`orig`を`int`に変換し、`min`と`max`内に収める。

        プライベートメソッド想定。
        `orig`が`int`に変換できなかった場合は例外を発生させる。

        Args:
            orig (int like): clip対象の値。
            min: 最小値。
            max: 最大値。

        Return:
            変換済みの値。
        """
        try:
            orig = int(orig)
        except ValueError:
            raise ValueError(f"(ARIES) error: '{orig}' is not int.")
        else:
            if orig > max:
                print(f"(ARIES) warn: {orig} is limited to {max}.")
                return max
            elif orig < min:
                print(f"(ARIES) warn: {orig} is limited to {min}.")
                return min
            else:
                return orig

    def raw_command(self, cmd: str, timeout: int = 300) -> str:
        """'RPS1/4/90000/1'のような従来のコマンドをそのまま使用する。

        返答があるまで待機する。

        Args:
            cmd: telnetに送信するコマンド。
            timeout: 返答を待機する最大秒数。デフォルトは300秒。

        Return:
            生のコマンド実行結果。
        """
        self.tn.write(cmd.encode())
        self.tn.write(b"\r\n")

        # 改行されるまで待機して、得られた内容を返す
        return self.tn.read_until(b"\r\n", timeout).decode()

    def reset(self) -> None:
        """原点近接センサ・エッジを用いてステージを厳密に原点へ復帰させる。

        電源投入直後や長時間駆動させた後に実行することで、
        ステージ位置の信頼性を向上できる。
        """
        self.raw_command(f"ORG1/{self.__speed}/1")
        self.raw_command(f"ORG2/{self.__speed}/1")
        self.raw_command(f"ORG3/{self.__speed}/1")

    def sleep_until_stop(self) -> None:
        """ステージが停止状態になるまでsleepする。"""
        while not self.is_stopped:
            time.sleep(0.5)
        return

    def stop_all_stages(self, immediate: bool = False) -> None:
        """3軸全てを停止させる

        Args:
            immediate: Falseで減速停止、Trueで緊急停止
        """
        self.raw_command(f"STP1/{int(immediate)}")
        self.raw_command(f"STP2/{int(immediate)}")
        self.raw_command(f"STP3/{int(immediate)}")

    def unlock_emergency_stop(self) -> None:
        """非常停止信号のソフトウェアロックを解除する"""
        self.raw_command("REM")

    @property
    def is_stopped(self) -> bool:
        """3軸全てが停止状態であれば`True`"""
        return self.raw_command("STR1").split()[2] == "0" \
            and self.raw_command("STR2").split()[2] == "0" \
            and self.raw_command("STR3").split()[2] == "0"

    @property
    def x(self) -> int:
        """ARIESの1軸パルス値と連動。-45,000 〜 +45,000。"""
        return int(self.raw_command("RDP1").split()[2])

    @x.setter
    def x(self, x: int) -> None:
        x = self._clip(x, -45000, 45000)
        self.raw_command(f"APS1/{self.__speed}/{x}/1")
        time.sleep(self.INTERVAL_TIME)

    @property
    def y(self) -> int:
        """ARIESの2軸パルス値と連動。0 〜 +90,000。"""
        return int(self.raw_command("RDP2").split()[2])

    @y.setter
    def y(self, y: int) -> None:
        y = self._clip(y, 0, 90000)
        self.raw_command(f"APS2/{self.__speed}/{y}/1")
        time.sleep(self.INTERVAL_TIME)

    @property
    def z(self) -> int:
        """ARIESの3軸パルス値と連動。180,000で一周。-360,000 〜 +360,000。"""
        return int(self.raw_command("RDP3").split()[2])

    @z.setter
    def z(self, z: int) -> None:
        z = self._clip(z, -134217728, 134217727)
        self.raw_command(f"APS3/{self.__speed}/{z}/1")
        time.sleep(self.INTERVAL_TIME)

    @property
    def x_by_degree(self) -> float:
        """xを角度で読み書き。分解能は0.002度。"""
        return self.x / self.PULSE_PER_DEGREE_X

    @x_by_degree.setter
    def x_by_degree(self, x_by_degree: float) -> None:
        self.x = int(x_by_degree * self.PULSE_PER_DEGREE_X)

    @property
    def y_by_degree(self) -> float:
        """yを角度で読み書き。分解能は0.001度。"""
        return self.y / self.PULSE_PER_DEGREE_Y

    @y_by_degree.setter
    def y_by_degree(self, y_by_degree: float) -> None:
        self.y = int(y_by_degree * self.PULSE_PER_DEGREE_Y)

    @property
    def z_by_degree(self) -> float:
        """zを角度で読み書き。分解能は0.002度。"""
        return self.z / self.PULSE_PER_DEGREE_Z

    @z_by_degree.setter
    def z_by_degree(self, z_by_degree: float) -> None:
        self.z = int(z_by_degree * self.PULSE_PER_DEGREE_Z)

    @property
    def speed(self) -> int:
        """3軸全てのステージの移動速度。1〜9。"""
        return self.__speed

    @speed.setter
    def speed(self, speed: int) -> None:
        self.__speed = self._clip(speed, 0, 9)


def main() -> int:
    """コマンドラインツールとして使用するときの処理"""
    import argparse

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
    try:
        aries = Aries(host=args.host, port=args.port)
    except ConnectionError as err:
        # 接続失敗時は``ConnetionError`を投げる
        print(err)
        print("connection failed.")
        return 1
    else:
        print(f"connected to {args.host}:{args.port}.")

    # コマンドの実行と結果の表示
    result = aries.raw_command(args.command)
    print(result)

    # 明示的な切断要求(デストラクタがあるので書かなくても良い)
    del aries
    print("connection closed.")
    return 0


if __name__ == '__main__':
    main()
