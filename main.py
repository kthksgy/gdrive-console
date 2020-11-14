from __future__ import print_function
from pprint import pprint

import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from downloader import RecursiveDownloader

# アプリに必要な権限を設定
SCOPES = [
    # Google Driveの全ファイル読み込み専用
    'https://www.googleapis.com/auth/drive.readonly'
]

credentials = None
# 認証トークンがあれば読み込む
if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
        credentials = pickle.load(token)

# 認証情報が有効でなければGoogleのログイン画面を開いて新たに生成
if not credentials or not credentials.valid:
    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'client_id.json', SCOPES)
        credentials = flow.run_local_server(port=0)
    # 取得したユーザーの認証情報を保存
    with open('token.pickle', 'wb') as token:
        pickle.dump(credentials, token)

# Google Drive API v3のオブジェクトを生成
service = build('drive', 'v3', credentials=credentials)
download = RecursiveDownloader(service)
Q_TYPE_FOLDER = "mimeType = 'application/vnd.google-apps.folder'"
Q_TYPE_NOT_FOLDER = "mimeType != 'application/vnd.google-apps.folder'"

d = {'/': 'root'}
pwd = '/'
while True:
    stdin = input(f'{pwd} > ')

    # アプリを終了
    if stdin == 'exit':
        exit()

    # 現在のフォルダ内のファイルとフォルダの一覧を取得
    if stdin == 'ls':
        page_token = None
        current = {}
        # フォルダの一覧を取得
        while True:
            response = service.files().list(
                q=Q_TYPE_FOLDER
                + f" and '{d[pwd]}' in parents",
                spaces='drive',
                fields='nextPageToken, files(id, name)',
                pageToken=page_token).execute()
            page_token = response.get('nextPageToken', None)
            current.update({f"{pwd}{i['name']}/": i['id'] for i in response.get('files', [])})
            if page_token is None:
                break
        # ファイルの一覧を取得
        while True:
            response = service.files().list(
                q=Q_TYPE_NOT_FOLDER
                + f" and '{d[pwd]}' in parents",
                spaces='drive',
                fields='nextPageToken, files(id, name)',
                pageToken=page_token).execute()
            page_token = response.get('nextPageToken', None)
            current.update({f"{pwd}{i['name']}": i['id'] for i in response.get('files', [])})
            if page_token is None:
                break
        d.update(current)
        pprint(current)

    # 指定したフォルダに移動
    if stdin.startswith('cd'):
        args = stdin.split(' ', maxsplit=1)
        if len(args) == 1:
            pwd = pwd[:pwd[:-1].rfind('/') + 1]
        elif len(args) == 2:
            td = f"{pwd}{stdin[len('cd '):]}/"
            if td in d:
                pwd = td
            else:
                print('そのようなディレクトリは存在しません。')

    # 現在のフォルダの中身を全てダウンロード
    if stdin.startswith('download'):
        args = stdin.split(' ', maxsplit=1)
        if len(args) == 2:
            td = args[1]
        else:
            dirs = pwd[:-1].rsplit('/', maxsplit=1)
            td = dirs[1] if len(dirs) == 2 else 'root'
        download(td, d[pwd])
