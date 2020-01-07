"""aries.pyのモジュールとしての使用例"""

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

    aries.speed = 5  # 5速で駆動する

    print("reseting stage position")
    aries.reset()  # 初期位置に戻す
    aries.sleep_until_stop()  # 停止するまで待機する

    def direction(int_val):
        if int_val % 2 == 0:
            return 1
        else:
            return -1

    # パルス値による指定
    for i in range(4):
        aries.x = 45000 * direction(i)
        aries.sleep_until_stop()
        for j in range(10):
            print(f"shot {aries.x},{aries.y}")
            aries.x += -10000 * direction(i)
            aries.sleep_until_stop()
        aries.y += 30000

    print("reseting stage position")
    aries.reset()
    aries.sleep_until_stop()

    # 角度による指定
    '''
    for i in range(4):
        for j in range(10):
            print(f"shot {aries.z_by_degree},{aries.y_by_degree}")
            aries.z_by_degree += 60.0
            aries.sleep_until_stop()
        aries.y_by_degree += 30.0
    '''

    return 0


if __name__ == '__main__':
    main()
