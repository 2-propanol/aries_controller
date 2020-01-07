# ARIES / LYNX モーターコントローラのpython制御
[神津精機株式会社](https://www.kohzu.co.jp/i/)さんの[ARIES / LYNX ドライバ分離型多軸モーターコントローラ](https://www.kohzu.co.jp/products/control-electronics/motor-controller-kosmos/aries-lynx/)をPythonで制御します。
telnetのラッパーです。
研究室の3軸ステージの制御用に作成。
Pythonの`telnetlib`モジュールを使うため、`telnet`コマンドがインストールされていなくても実行が可能です。


## コマンドラインツール互換
```
python3 aries.py --host <HOST> --port <PROT> <operation>
```
とするとARIESにコマンドを送信できます。

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

- `raw_command()`  
    telnetで使用できるコマンドをそのまま実行する
- `reset()`  
    3軸全てを原点へ復帰させる
- `sleep_until_stop()`  
    3軸全てが停止するまで`time.sleep()`する


### ステージ位置制御
クラスのメンバ`x`, `y`, `z`(および`x_by_degree`, `y_by_degree`, `z_by_degree`)は3軸それぞれの位置と**連動**しています。
```
x (int): ARIESの1軸パルス値と連動。-45,000 〜 +45,000。
y (int): ARIESの2軸パルス値と連動。0 〜 +90,000。
z (int): ARIESの3軸パルス値と連動。180,000で一周。-360,000 〜 +360,000。
x_by_degree (float): xを角度で読み書き。分解能は0.002度。
y_by_degree (float): yを角度で読み書き。分解能は0.001度。
z_by_degree (float): zを角度で読み書き。分解能は0.002度。
```
よって、
```python
aries.x_by_degree += 30
```
のような`+=`, `-=`を使った相対位置駆動が出来ます。  
ただし、変数への代入はノンブロッキング処理としているため、
```python
aries.x_by_degree += 30

print(aries.x_by_degree)  # 0.0372
time.sleep(1)
print(aries.x_by_degree)  # 20.36
time.sleep(1)
print(aries.x_by_degree)  # 30.0
```
のように相対位置駆動を要求した直後は移動中の値が返されます。

よって、確実な値が必要な場合は`aries.sleep_until_stop()`を使って移動完了まで待つか、一時変数を使ってください。
```python
aries.x_by_degree += 30

aries.sleep_until_stop()

print(aries.x_by_degree)  # 30.0
time.sleep(1)
print(aries.x_by_degree)  # 30.0
```
```python
x = 30.0
aries.x_by_degree = x

print(x)  # 30.0
print(aries.x_by_degree)  # 0.228

aries.sleep_until_stop()

print(x)  # 30.0
print(aries.x_by_degree)  # 30.0
```
