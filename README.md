# 玉川大学脳科学トレーニングコース  
## げっ歯類を用いた脳システム研究法コース

## 概要

本リポジトリでは、**Neuropixelsで計測し、スパイクソーティングされた神経活動データを用いた基本的な解析**を行います。

はじめに、神経活動データと行動データを同じ時間軸上で扱うための**同期（synchronization）**について、ダイジェスト形式で説明します。神経活動と刺激提示、選択行動、報酬などの行動イベントを正確に対応付けることは、神経活動解析だけでなく、実験系を構築する上でも重要な要素です。

次に、スパイクソーティングによって得られた各ユニット（推定された単一ニューロン活動）について、**Quality Metrics**を計算します。発火率、ISI violation、presence ratioなどの指標を用いて各ユニットの特徴や記録品質を可視化し、解析に用いるユニットについて検討します。

その後、神経活動を可視化する基本的な方法である **PETH（Peri-Event Time Histogram）** を用いて、各ユニットの活動を解析します。刺激提示、選択行動、報酬などのイベントを基準としてスパイク活動を整列することで、それぞれのユニットが課題中のどのイベントに対してどのような活動パターンを示すかを観察し、その神経表現について考察します。

さらに、各ユニットの活動パターンを用いた**簡単なクラスタリング解析**を行います。類似した活動パターンを持つユニットをグループ化することで、集団ニューロン活動の特徴を可視化し、どのような機能的なニューロン集団が存在する可能性があるかを観察・考察します。

本トレーニングでは、主に以下の流れで解析を行います。

1. **神経活動データと行動データの同期**

   * Neuropixelsの神経活動データと行動イベントの時間軸を対応付ける
   * 神経活動と行動を同期して記録・解析する考え方を理解する

2. **Quality Metricsによるユニットの評価**

   * スパイクソーティング済みの各ユニットについてQuality Metricsを計算する
   * 各ユニットの特徴や記録品質を可視化・検討する

3. **PETHによる神経活動の可視化**

   * 行動イベントを基準として各ユニットのスパイク活動を整列する
   * イベントに伴う発火活動の時間変化を観察する

4. **各ユニットの神経表現の観察・考察**

   * 刺激、選択行動、報酬などに関連した活動パターンを確認する
   * 各ユニットがどのような情報を表現している可能性があるかを考察する

5. **神経活動パターンのクラスタリング**

   * 各ユニットの活動パターンを特徴量としてクラスタリングする
   * 類似した活動を示すユニットをグループ化する

6. **集団ニューロン活動の可視化・考察**

   * クラスタごとの活動パターンを比較する
   * 集団ニューロン活動にどのような特徴があるかを観察・考察する

---

## 環境構築

以下では、上記の解析を実行するために必要なPython環境をWindows上に構築します。

解析環境には **Python 3.12.3** と **Poetry** を使用します。Poetryを用いて、本リポジトリで使用するPythonパッケージを管理し、プロジェクト専用の仮想環境 `.venv` を作成します。

また、作成した仮想環境をJupyter NotebookおよびVS Codeから使用できるように、Jupyter kernelとして登録します。

環境構築は以下の流れで行います。

1. Gitをインストールする
2. GitHubから本リポジトリをダウンロードする
3. Python 3.12.3をインストールする
4. Poetryをインストールする
5. プロジェクト専用の仮想環境 `.venv` を作成する
6. 解析に必要なPythonパッケージをインストールする
7. Jupyter Notebook / VS Codeで使用するkernelを登録する

> [!IMPORTANT]
> このREADMEでは、Windowsのユーザー名を `<username>` と表記します。
>
> コマンドを実行する際は、**`<username>` を各自のWindowsユーザー名に置き換えてください。**
>
> 例えば、Windowsユーザー名が `User1` の場合、
>
> ```text
> C:\Users\<username>\AppData\Local\Programs\Python\Python312\python.exe
> ```
>
> は、
>
> ```text
> C:\Users\User1\AppData\Local\Programs\Python\Python312\python.exe
> ```
>
> のように置き換えます。
>
> 自分のWindowsユーザー名が分からない場合は、PowerShellで以下を実行すると確認できます。
>
> ```powershell
> $env:USERNAME
> ```

---

### 1. Gitをインストールする

以下からGit for Windowsをダウンロードしてインストールします。

https://git-scm.com/install/windows

---

### 2. リポジトリをダウンロードする

Git Bashを開き、リポジトリを保存するディレクトリへ移動します。

```bash
cd /c/Users/<username>/tamagawa-neuro-traing-course-20XX/
```

> [!NOTE]
> `<username>` は各自のWindowsユーザー名に置き換えてください。
>
> また、`tamagawa-neuro-traing-course-20XX` の部分も、実際に使用するフォルダ名に合わせて変更してください。

リポジトリをクローンします。

```bash
git clone https://github.com/NeuralDynamics-Tamagawa/tamagawa-neuro-training-shysgmt.git
```

---

### 3. Python 3.12.3をインストールする

以下からPython 3.12.3をダウンロードします。

https://www.python.org/downloads/release/python-3123/

インストール時には、

```text
Add python.exe to PATH
```

にチェックを入れてください。

---

### 4. PowerShellを使って環境構築する

以降の操作はPowerShellで行います。

#### 4.1 Pythonの場所を確認する

```powershell
where /R C:\Users\<username> python.exe
```

例えば以下のように表示されます。

```text
C:\Users\<username>\AppData\Local\Microsoft\WindowsApps\python.exe
C:\Users\<username>\AppData\Local\Microsoft\WindowsApps\Microsoft.DesktopAppInstaller_8wekyb3d8bbwe\python.exe
C:\Users\<username>\AppData\Local\Programs\Python\Python312\python.exe
C:\Users\<username>\AppData\Local\Programs\Python\Python312\Lib\venv\scripts\nt\python.exe
```

今回使用するPythonは、例えば以下です。

```text
C:\Users\<username>\AppData\Local\Programs\Python\Python312\python.exe
```

`WindowsApps` 内の `python.exe` ではなく、実際にインストールしたPythonを使用してください。

---

#### 4.2 pipのバージョンを確認する

以下のコマンドを実行して、pipが正しく使用できることを確認します。

```powershell
python -m pip --version
```

正常に設定されている場合は、以下のようにpipのバージョンとインストール先が表示されます。

```text
pip 24.0 from C:\Users\<username>\AppData\Local\Programs\Python\Python312\Lib\site-packages\pip (python 3.12)
```

バージョン番号は環境によって異なりますが、`pip ... (python 3.12)` のような情報が表示されれば問題ありません。

また、PythonへのPATHが正しく設定されているかは、以下でも確認できます。

```powershell
where python
```

正常にPATHが設定されている場合は、例えば以下のようにPythonのパスが表示されます。

```text
C:\Users\<username>\AppData\Local\Programs\Python\Python312\python.exe
```

> [!NOTE]
> **`python` とだけ表示される、またはPythonのパスが表示されない場合**
>
> `python -m pip --version` を実行しても、
>
> ```text
> python
> ```
>
> とだけ表示される場合や、`where python` で目的のPythonが表示されない場合は、PythonへのPATHが正しく設定されていない可能性があります。
>
> まず、Python 3.12.3のインストーラーを再度起動し、**Modify** を選択してください。
>
> その後、**Add Python to environment variables** を有効にしてインストールを完了します。
>
> 設定後はPowerShellを一度閉じて再度開き、
>
> ```powershell
> where python
> ```
>
> および
>
> ```powershell
> python -m pip --version
> ```
>
> を再実行してください。

> [!TIP]
> **Windowsの環境変数から手動でPATHを追加する方法**
>
> Pythonインストーラーから設定できない場合は、Windowsの環境変数から手動でPATHを追加することもできます。
>
> 1. Windowsの検索欄で **「環境変数」** と検索する
> 2. **「システム環境変数の編集」** を開く
> 3. **「環境変数」** をクリックする
> 4. 「ユーザー環境変数」の **`Path`** を選択する
> 5. **「編集」** をクリックする
> 6. **「新規」** を選択して、Pythonのインストール先を追加する
>
> 例：
>
> ```text
> C:\Users\<username>\AppData\Local\Programs\Python\Python312\
> ```
>
> あわせて、以下の `Scripts` フォルダも追加しておくと便利です。
>
> ```text
> C:\Users\<username>\AppData\Local\Programs\Python\Python312\Scripts\
> ```
>
> **複数のPythonがインストールされている場合は、今回使用するPythonのパスをできるだけ上に移動してください。**
>
> WindowsのPATHでは、基本的に**上に登録されているパスほど優先して検索されます**。そのため、古いPythonや `WindowsApps` のPythonが上にあると、意図しないPythonが実行される場合があります。
>
> 「上へ移動」を使って、例えば以下の2つを上側に配置します。
>
> ```text
> C:\Users\<username>\AppData\Local\Programs\Python\Python312\
> C:\Users\<username>\AppData\Local\Programs\Python\Python312\Scripts\
> ```
>
> 設定後は、開いているPowerShellやコマンドプロンプトを一度閉じて、再度起動してください。
>
> その後、以下を実行して確認します。
>
> ```powershell
> where python
> ```
>
> 先頭に以下のようなパスが表示されていれば、今回使用するPythonが優先されています。
>
> ```text
> C:\Users\<username>\AppData\Local\Programs\Python\Python312\python.exe
> ```
>
> さらに、
>
> ```powershell
> python --version
> ```
>
> を実行して、
>
> ```text
> Python 3.12.3
> ```
>
> のように表示されれば問題ありません。
>
> 環境変数の設定画面は、`Win + R` を押して、
>
> ```text
> sysdm.cpl
> ```
>
> と入力し、
>
> ```text
> 詳細設定 → 環境変数
> ```
>
> と進む方法でも開けます。



#### 4.3 Poetryをインストールする

```powershell
python -m pip install poetry
```

インストールできたことを確認します。

```powershell
poetry --version
```

---

#### 4.4 プロジェクトフォルダへ移動する

```powershell
cd C:\Users\<username>\tamagawa-neuro-traing-course-20XX\tamagawa-neuro-training-shysgmt
```

実際の保存場所に合わせて変更してください。

---

#### 4.5 `.venv` をプロジェクト内に作成するよう設定する

```powershell
poetry config virtualenvs.in-project true --local
```

これにより、プロジェクトフォルダ内に `.venv` が作成されます。

---

#### 4.6 使用するPythonを指定する

例：

```powershell
poetry env use C:\Users\<username>\AppData\Local\Programs\Python\Python312\python.exe
```

Pythonのパスは、それぞれのPCで確認したものに変更してください。

> [!IMPORTANT]
> 上記のパスをそのままコピーするのではなく、**4.1で確認した自分のPCのPythonパスを指定してください。**

---

#### 4.7 Python環境を作成する

```powershell
poetry install
```

`pyproject.toml` および `poetry.lock` に記載されているパッケージがインストールされます。

---

#### 4.8 Jupyter用kernelを登録する

Poetry環境内のPythonを、Jupyter NotebookやVS Codeから使用できるようにkernelとして登録します。

```powershell
poetry run python -m ipykernel install --user --name tmgw-neuro-train --display-name "Python (tmgw-neuro-train)"
```

Jupyter NotebookやVS Codeでは、通常は以下のkernelを選択します。

```text
Python (tmgw-neuro-train)
```

> [!NOTE]
> **`Python (tmgw-neuro-train)` が表示されない場合**
>
> VS Codeでは、登録したkernel名ではなく、プロジェクト内の `.venv` がPython環境として表示される場合があります。
>
> その場合は、`.venv` に対応するPythonを選択すれば問題ありません。
>
> 例えば、以下のように表示されることがあります。
>
> ```text
> .venv (Python 3.12.x)
> ```
>
> または
>
> ```text
> Python 3.12.x ('.venv')
> ```
>
> VS Codeでは、**Microsoft製のPython拡張機能**がインストールされていることを確認してください。
>
> Notebookを使用する場合は、**Microsoft製のJupyter拡張機能**もインストールしてください。
>
> 選択しているPython環境が正しいか確認するには、Notebook上で以下を実行します。
>
> ```python
> import sys
> print(sys.executable)
> ```
>
> 出力が以下のように、プロジェクト内の `.venv` を指していれば正しく設定されています。
>
> ```text
> ...\tamagawa-neuro-training-shysgmt\.venv\Scripts\python.exe
> ```
>
> `AppData\Local\Programs\Python\Python312\python.exe` など、PC本体にインストールしたPythonではなく、**プロジェクト内の `.venv\Scripts\python.exe` を使用してください。**

---

#### 4.9 環境を確認する

Poetryが使用している環境を確認します。

```powershell
poetry env info
```

Jupyter Notebook上では以下を実行します。

```python
import sys

print(sys.executable)
print(sys.version)
```

`.venv\Scripts\python.exe` が表示されていれば、正しい仮想環境が使用されています。

---

#### セットアップコマンドまとめ

以下のコマンドを上から順番に実行することで環境を構築できます。

> [!IMPORTANT]
> 以下の `<username>` は、**各自のWindowsユーザー名に置き換えてから実行してください。**

```powershell
# Pythonの場所を確認
where /R C:\Users\<username> python.exe

# pipを確認
python -m pip --version

# Poetryをインストール
python -m pip install poetry

# Poetryのバージョンを確認
poetry --version

# プロジェクトフォルダへ移動
cd C:\Users\<username>\tamagawa-neuro-traing-course-20XX\tamagawa-neuro-training-shysgmt

# .venvをプロジェクト内に作成するよう設定
poetry config virtualenvs.in-project true --local

# 使用するPythonを指定
poetry env use C:\Users\<username>\AppData\Local\Programs\Python\Python312\python.exe

# 必要なパッケージをインストール
poetry install

# Jupyter kernelを登録
poetry run python -m ipykernel install --user --name tmgw-neuro-train --display-name "Python (tmgw-neuro-train)"
```

---

### 5. セットアップ完了

Jupyter NotebookまたはVS Codeで、

```text
Python (tmgw-neuro-train)
```

またはプロジェクト内の `.venv` に対応するPython環境を選択し、以下を実行してください。

```python
import sys
print(sys.executable)
```

以下のように、プロジェクト内の `.venv` が表示されればセットアップ完了です。

```text
...\tamagawa-neuro-training-shysgmt\.venv\Scripts\python.exe
```
