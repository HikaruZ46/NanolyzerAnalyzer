from setuptools import setup, find_packages

setup(
    name='NanolyzerAnalyzer',  # パッケージ名（pip listで表示される）
    version="0.0.3",  # バージョン
    description="Nanolyzerで出てきたデータを解析するためのパッケージ",  # 説明
    author='Hikaru Nozawa',  # 作者名
    packages=find_packages(),  # 使うモジュール一覧を指定する
    license='MIT'  # ライセンス
)
