# ARIES 3軸ステージをpythonで制御する
telnetの煩わしさを解消する目的で作成。
ARIESの3軸ステージをPythonから制御できます。
Pythonの`telnetlib`モジュールを使うため、`telnet`コマンドがインストールされていなくても実行が可能です。

## コマンドラインツール互換
```
python3 aries.py --host <HOST> --port <PROT> <operation>
```
あるいは、Unix系では実行権限をつけた上で
```
./aries.py --host <HOST> --port <PROT> <operation>
```
とするとワンライナーでARIESにコマンドを送信できます。

`HOST`, `PORT`は省略した場合、`192.168.1.20`, `12321`が使われます。

## Pythonモジュールとして利用
example.pyに使用例があります。基本的に
```
from aries import Aries
```
で`import`し、
```
stage = Aries()
```
のようにインスタンスを作って (インスタンス作成時に接続要求が行われ、待機時間が発生します)
```
stage.raw_command("RPS2/4/45000/1")
```
を実行してステージを操作する流れになります。

telnetの切断はPython終了時(インスタンスが破棄されるとき)に自動で行われるため明示的に切断要求を出す必要はありません。

### 実装済みメソッド
詳しい説明は aries.py の Docstring に記載しています。

- raw_command  
    telnetで使用できるコマンドをそのまま実行する
