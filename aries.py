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
import subprocess
import time


def main():
    args = sys.argv

    print(args)
    print("第1引数：" + args[1])
    print("第2引数：" + args[2])
    print("第3引数：" + args[3])

    commandlist = ["telnet"] + ["192.168.1.20"]
    p = subprocess.Popen(commandlist,
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    # Adding this for sync to avoid any overlap
    time.sleep(1)
    p.communicate("RPS1/1/9000/1\n")

    return 0


if __name__ == '__main__':
    main()
