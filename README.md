# tamagawa-neuro-training-shysgmt







### 環境構築

#### python3.12.3をダウンロード
https://www.python.org/downloads/release/python-3123/

インストールしたPythonがどこにあるか確認（このパスをメモしておく）
```
where /R C:\Users\rodentia01 python.exe
```
```
C:\Users\rodentia01>where /R C:\Users\rodentia01 python.exe
C:\Users\rodentia01\AppData\Local\Microsoft\WindowsApps\python.exe
C:\Users\rodentia01\AppData\Local\Microsoft\WindowsApps\Microsoft.DesktopAppInstaller_8wekyb3d8bbwe\python.exe
C:\Users\rodentia01\AppData\Local\Programs\Python\Python312\python.exe
C:\Users\rodentia01\AppData\Local\Programs\Python\Python312\Lib\venv\scripts\nt\python.exe
```

```
C:\Users\rodentia01\AppData\Local\Programs\Python\Python312\python.exe

```
をパスに指定する。

#### pipのverを確認する
```
python -m pip --version
```

#### poetryをインストール
```
pip install poetry
```

#### .venvの作成

- プロジェクトフォルダに移動する。
```
cd hogehoge/tc2025_shysgmt
```

- プロジェクトフォルダ内に.venvを作成するように設定する
```
poetry config virtualenvs.in-project true --local
```

- pythonを指定して.venvを作成する（pythonが入っているフォルダを指定）
<br>例：C:\Users\rodentia01\AppData\Local\Programs\Python\Python312\python.exe
<br>（<u>User1のところは自分のパソコンに合わせる</u>）
```
poetry env use C:\Users\rodentia01\AppData\Local\Programs\Python\Python312\python.exe
```

- 環境を作成する。
```
poetry install
```

- ipykernelをインストールする
```
poetry run python -m ipykernel install --user --name tc2025_shysgmt
```
