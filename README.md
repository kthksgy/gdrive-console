# Google Drive コンソール
PythonでGoogle DriveにアクセスするCUIアプリです。

## 動作環境
- Python `>= 3.8`
  - `google-api-python-client >= 1.23`
  - `google-auth-httplib2 >= 0.0`
  - `google-auth-oauthlib >= 0.4`

```bash
$ pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

## 機能
- [x] フォルダ内のファイルの再帰的なダウンロード

### 未実装の機能
- [ ] ファイル単体のダウンロード
- [ ] 並列ダウンロード
- [ ] アップロード
- [ ] パスに使えない文字への対応

## 使用方法
[Google Developer Console](https://console.developers.google.com/)からCUI用の認証情報を取得して、<br>
`main.py`と同じ階層に`client_id.json`として保存してください。

```bash
$ python main.py
```

### `ls`
現在のフォルダに入っているファイルとフォルダの一覧を取得します。

```plaintext
/ > ls
```

### `cd [移動先のフォルダ名]`
指定したフォルダに移動します。<br>
事前に`ls`コマンドでフォルダの一覧を取得しておかないといけません。

### `download [ディレクトリ名]`
現在のフォルダの中身を再帰的にダウンロードします。<br>
ディレクトリ名を省略すると、現在のフォルダの名前のディレクトリを作成します。

### `exit`
アプリを終了します。

## 参考
- [Google Developer Console](https://console.developers.google.com/)