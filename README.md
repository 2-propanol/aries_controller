# ARIES 3軸ステージをpythonで制御する
telnetの煩わしさを解消する目的で作成。
ARIESの3軸ステージをPythonから制御できます。
Pythonの`telnetlib`モジュールを使うため、`telnet`コマンドがインストールされているかにどうかにかかわらず実行が可能です。

## コマンドラインツール互換
```
python3 aries.py --host <HOST> --port <PROT> <operation>
```
あるいは、Unix系では実行権限をつけた上で
```
./aries.py --host <HOST> --port <PROT> <operation>
```
とするとワンライナーでARIESにコマンドを送信できます。

`HOST`, `PORT`は省略した場合、192.168.1.20, 12321が使われます。
