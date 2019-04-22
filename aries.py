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
import telnetlib
# import time


def main():
    args = sys.argv

    print(args)
    print("第1引数：" + args[1])
    print("第2引数：" + args[2])
    print("第3引数：" + args[3])

    HOST = "192.168.1.20"
    PORT = "12321"

    tn = telnetlib.Telnet(HOST, PORT)

    # tn.write(b"RPS1/2/9000/1\r\n")
    tn.write(b"ORG1/3/1\r\n")

    print(tn.read_all().decode('ascii'))

    return 0


if __name__ == '__main__':
    main()
