"""aries.pyのモジュールとしての使用例"""

from time import sleep

from aries import Aries


def main():
    # ARIESへの接続を試みる(2秒待機して3回まで再試行する)
    for i in range(3):
        try:
            print("Trying 192.168.1.20:12321.")
            stage = Aries()
        except ConnectionError as err:
            # 接続失敗時は`ConnetionError`を投げる
            print(err)
            sleep(2)
        else:
            print(f"connected to 192.168.1.20:12321.")
            break
    else:
        # 3回とも接続に失敗した(`break`されなかった)
        print("connection failed.")
        return 1

    stage.speed = 5  # 5速で駆動する

    stage.position = (0, 90, 0, 20)
    stage.sleep_until_stop()  # 停止するまで待機する

    x, y, _, _ = stage.position

    def direction(int_val):
        if int_val % 2 == 0:
            return 1
        else:
            return -1

    # パルス値による指定
    for i in range(4):
        x = 90 * direction(i)
        stage.position = (x, y, 0, 20)
        stage.sleep_until_stop()
        for j in range(10):
            print(f"shot {x},{y}")
            x += -20 * direction(i)
            stage.position = (x, y, 0, 20)
            stage.sleep_until_stop()
        y -= 30
        stage.position = (x, y, 0, 20)

    print("reseting stage position")
    stage.reset()
    stage.sleep_until_stop()

    return 0


if __name__ == '__main__':
    main()
