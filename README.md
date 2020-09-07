# ARIES / LYNX モーターコントローラのpython制御
[神津精機株式会社](https://www.kohzu.co.jp/i/)さんの[ARIES / LYNX ドライバ分離型多軸モーターコントローラ](https://www.kohzu.co.jp/products/control-electronics/motor-controller-kosmos/aries-lynx/)をPythonで制御します。

研究室の3軸ステージの制御用に作成。


## Usage
環境次第で`pip`を`pip3`や`pipenv`、`pip install`を`poetry add`などに読み替えてください。

### Install
```bash
pip install git+https://github.com/2-propanol/aries_python
```

### Update
```bash
pip install -U aries_python
```

### `aries`(コマンドラインツール)
```
aries --host <HOST> --port <PORT> <operation>
```

> `HOST`, `PORT`は省略した場合、`192.168.1.20`, `12321`が使われます。

### `import`(Pythonモジュール)
```python
>>> from aries import Aries
>>> stage = Aries()

>>> print(stage.position)
(0.0, 0.0, 0.0)

>>> stage.raw_command("RPS2/4/45000/1")
>>> print(stage.position)
(0.0, 45.0, 0.0)
```

### Uninstall
```bash
pip uninstall aries_python
```
