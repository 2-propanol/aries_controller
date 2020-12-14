"""ARIES 4軸ステージをPythonで制御する

Usage: aries --host <HOST> --port <PROT> <operation>

<HOST>
    ARIESのIPアドレス。省略すると 192.168.1.20 が使用される。

<PORT>
    ARIESのポート番号。省略すると 12321 が使用される。

<operation>
    ARIESに送信するコマンド。RPS1/4/90000/1 など。省略不可。
"""

from socket import timeout as socket_timeout
from sys import stderr
from telnetlib import Telnet
from time import sleep
from typing import Sequence, Tuple


class Aries:
    """ARIES 4軸ステージを制御するクラス

    1軸(パン): -90度 〜 +90度(分解能 0.002度)、パルス値 -45,000 〜 +45,000。
    2軸(チルト): 0度 〜 90度(分解能 0.001度)、パルス値 0 〜 +90,000。
    3軸(ロール): 360度無限回転(分解能 0.002度)、パルス値 0 〜 +180,000(180,000で一周)。
    4軸(光源): 360度無限回転(分解能 0.002度)、パルス値 -90,000 〜 +90,000(180,000で一周)。

    Attributes:
        is_stopped (bool): 4軸全てが停止していればTrue。Read-Only。
        speed (int): 4軸全てのステージの移動速度。1〜9。
        position (Sequence[float]): 各軸の角度と連動。
        position_by_pulse (Sequence[int]): 各軸のパルス値と連動。
        ignore_safety_stop (bool): デストラクト時に非常停止信号を発行しない。デフォルトはFalse。
        allow_u_axis_shortest_move (bool): U軸(光源軸)の無限回転を許可する。デフォルトはFalse。
    """

    __speed: Tuple[int, int, int, int] = [5, 5, 7, 4]

    # 駆動要求を発行した後の待機時間
    INTERVAL_TIME: float = 0.1

    # 各軸の分解能
    __PULSE_PER_DEGREE_X: int = 500
    __PULSE_PER_DEGREE_Y: int = 1000
    __PULSE_PER_DEGREE_Z: int = 500
    __PULSE_PER_DEGREE_U: int = 500

    # U軸(光源軸)の範囲
    __min_u_axis_pulse: int = -90000
    __max_u_axis_pulse: int = 90000

    # デストラクト時に非常停止を発行しない
    ignore_safety_stop: bool = False

    def __init__(
        self, host: str = "192.168.1.20", port: int = 12321, timeout: int = 10
    ) -> None:
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
        """各軸の駆動を停止し、telnetから切断。

        `KeyboardInterrupt`などを非常停止として機能させることが出来る。
        """
        try:
            if self.ignore_safety_stop and not self.is_stopped:
                self.stop_all_stages(immediate=True)
            self.tn.close()
        except AttributeError:
            # そもそもtelnetに接続されなかったときの例外
            pass

    @staticmethod
    def _clip(src: int, min_val: int, max_val: int) -> int:
        """`src`を、`min_val`と`max_val`内に収める。

        `src`が`int`でなかった場合は`TypeError`を投げる。

        Args:
            src: clip対象の値。
            min_val: 最小値。
            max_val: 最大値。

        Return:
            変換済みの値。
        """
        if type(src) is not int:
            raise TypeError(f"(ARIES) error: '{src}' is not int.")
        else:
            if src > max_val:
                print(f"(ARIES) warn: {src} is limited to {max_val}.", file=stderr)
                return max_val
            elif src < min_val:
                print(f"(ARIES) warn: {src} is limited to {min_val}.", file=stderr)
                return min_val
            else:
                return src

    @property
    def allow_u_axis_shortest_move(self) -> bool:
        if self.__min_u_axis_pulse == -90000 and self.__max_u_axis_pulse == 90000:
            return False
        elif (
            self.__min_u_axis_pulse == -134217728
            and self.__max_u_axis_pulse == 134217728
        ):
            return True
        else:
            raise RuntimeError(
                "'__min_u_axis_pulse' and '__max_u_axis_pulse' has an invalid value.\n"
                f"'__min_u_axis_pulse' has {self.__min_u_axis_pulse}, "
                f"'__max_u_axis_pulse' has {self.__max_u_axis_pulse}."
            )

    @allow_u_axis_shortest_move.setter
    def allow_u_axis_shortest_move(self, is_on: bool) -> None:
        if is_on:
            self.__min_u_axis_pulse = -134217728
            self.__max_u_axis_pulse = 134217728
        else:
            self.__min_u_axis_pulse = -90000
            self.__max_u_axis_pulse = 90000

    def raw_command(self, cmd: str, timeout: int = 300) -> str:
        """'RPS1/4/90000/1'のようなtelnet用コマンドを送信する。

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
        self.raw_command(f"ORG1/{self.__speed[0]}/1")
        self.raw_command(f"ORG2/{self.__speed[1]}/1")
        self.raw_command(f"ORG3/{self.__speed[2]}/1")
        self.raw_command(f"ORG4/{self.__speed[3]}/1")

    def sleep_until_stop(self) -> None:
        """ステージが停止状態になるまでsleepする。"""
        while not self.is_stopped:
            sleep(0.5)
        return

    def stop_all_stages(self, immediate: bool = False) -> None:
        """4軸全てを停止させる

        Args:
            immediate: Falseで減速停止、Trueで緊急停止
        """
        self.raw_command(f"STP1/{int(immediate)}")
        self.raw_command(f"STP2/{int(immediate)}")
        self.raw_command(f"STP3/{int(immediate)}")
        self.raw_command(f"STP4/{int(immediate)}")

    def unlock_emergency_stop(self) -> None:
        """非常停止信号のソフトウェアロックを解除する"""
        self.raw_command("REM")

    @property
    def is_stopped(self) -> bool:
        """4軸全てが停止状態であれば`True`"""
        return (
            self.raw_command("STR1").split()[2] == "0"
            and self.raw_command("STR2").split()[2] == "0"
            and self.raw_command("STR3").split()[2] == "0"
            and self.raw_command("STR4").split()[2] == "0"
        )

    @property
    def position_by_pulse(self) -> Tuple[int, int, int, int]:
        """各軸のパルス値と連動。インデックス単位での書き込みは出来ない。

        Example:
            >>> Aries.position_by_pulse
            (0, 0, 0, 0)
            >>> Aries.position_by_pulse[3] = 45000
            <NG (TypeError)>
            >>> Aries.position_by_pulse = [0,0,0,45000]
            <OK>
        """
        x = int(self.raw_command("RDP1").split()[2])
        y = int(self.raw_command("RDP2").split()[2])
        z = int(self.raw_command("RDP3").split()[2])
        u = int(self.raw_command("RDP4").split()[2])
        return (x, y, z, u)

    @position_by_pulse.setter
    def position_by_pulse(self, position: Sequence[int]) -> None:
        x = self._clip(position[0], -45000, 45000)
        y = self._clip(position[1], 0, 90000)
        z = self._clip(position[2], -134217728, 134217727)
        u = self._clip(position[3], self.__min_u_axis_pulse, self.__max_u_axis_pulse)

        last_pos = self.position_by_pulse
        if last_pos[0] != x:
            self.raw_command(f"APS1/{self.__speed[0]}/{x}/1")
            sleep(self.INTERVAL_TIME)
        if last_pos[1] != y:
            self.raw_command(f"APS2/{self.__speed[1]}/{y}/1")
            sleep(self.INTERVAL_TIME)
        if last_pos[2] != z:
            # 最短距離移動（例:20度から340度へ移動する場合、-40度移動を発行する）
            current_z = int(self.raw_command("RDP3").split()[2])
            distance = z - current_z
            distance = (distance + 90000) % 180000 - 90000
            self.raw_command(f"RPS3/{self.__speed[2]}/{distance}/1")
            sleep(self.INTERVAL_TIME)
        if last_pos[3] != u:
            self.raw_command(f"APS4/{self.__speed[3]}/{u}/1")
            sleep(self.INTERVAL_TIME)

    @property
    def position(self) -> Tuple[float, float, float, float]:
        """各軸の角度と連動。インデックス単位での書き込みは出来ない。

        Example:
            >>> Aries.position
            (0.0, 0.0, 0.0, 0.0)
            >>> Aries.position[3] = 90
            <NG (TypeError)>
            >>> Aries.position = [0,0,0,90]
            <OK>
        """
        position = self.position_by_pulse
        x = position[0] / self.__PULSE_PER_DEGREE_X
        y = position[1] / self.__PULSE_PER_DEGREE_Y
        z = (position[2] / self.__PULSE_PER_DEGREE_Z) % 180000
        u = position[3] / self.__PULSE_PER_DEGREE_U
        return (x, y, z, u)

    @position.setter
    def position(self, position: Sequence[float]) -> None:
        position = (
            int(position[0] * self.__PULSE_PER_DEGREE_X),
            int(position[1] * self.__PULSE_PER_DEGREE_Y),
            int(position[2] * self.__PULSE_PER_DEGREE_Z),
            int(position[3] * self.__PULSE_PER_DEGREE_U),
        )
        self.position_by_pulse = position

    @property
    def speed(self) -> Tuple[int]:
        """4軸全てのステージの移動速度。0〜9。"""
        return tuple(self.__speed)

    @speed.setter
    def speed(self, speed: Sequence[int]) -> None:
        self.__speed[0] = self._clip(speed[0], 0, 9)
        self.__speed[1] = self._clip(speed[1], 0, 9)
        self.__speed[2] = self._clip(speed[2], 0, 9)
        self.__speed[3] = self._clip(speed[3], 0, 9)


def main() -> int:
    """コマンドラインツールとして使用するときの処理"""
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("command", type=str, help="transfering command to ARIES")
    parser.add_argument(
        "--host",
        type=str,
        default="192.168.1.20",
        help="ARIES's IP address. default is 192.168.1.20",
    )
    parser.add_argument(
        "--port", type=int, default=12321, help="ARIES's port. default is 12321"
    )
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


if __name__ == "__main__":
    main()
