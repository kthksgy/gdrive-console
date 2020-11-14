import io
from pathlib import Path

from googleapiclient.http import MediaIoBaseDownload


class RecursiveDownloader:
    def __init__(self, service):
        '''
        Args:
            service: Google Drive APIのサービス
        '''
        self.service = service

    def __call__(self, path: str, dir_id: str):
        '''再帰的にダウンロードします。
        Args:
            path: ダウンロード先のディレクトリ
            dir_id: Google Drive内のフォルダのID
        Todo:
            * 並列ダウンロード
            * パスに使えない文字の処理
        '''
        # TODO: パスに使えない文字の処理
        Path(path).mkdir(exist_ok=True)
        if not path.endswith('/'):
            path += '/'
        page_token = None
        # フォルダは再帰呼び出し
        while True:
            response = self.service.files().list(
                q="mimeType = 'application/vnd.google-apps.folder'"
                f" and '{dir_id}' in parents",
                spaces='drive',
                fields='nextPageToken, files(id, name)',
                pageToken=page_token).execute()
            page_token = response.get('nextPageToken', None)
            for i in response.get('files', []):
                self(path + i['name'] + '/', i['id'])
            if page_token is None:
                break
        # ファイルはダウンロード
        while True:
            response = self.service.files().list(
                q="mimeType != 'application/vnd.google-apps.folder'"
                f" and '{dir_id}' in parents",
                spaces='drive',
                fields='nextPageToken, files(id, name)',
                pageToken=page_token).execute()
            page_token = response.get('nextPageToken', None)
            for i in response.get('files', []):
                file_path = Path(path + i['name'])
                if file_path.exists() and file_path.stat().st_size > 0:
                    print(f"{i['name']}は既に存在するためスキップします。")
                    continue
                done = False
                while done is False:
                    try:
                        print(f"{i['name']}をダウンロード中... ", end='')
                        # TODO: 並列ダウンロード
                        # TODO: パスに使えない文字の処理
                        with io.FileIO(file_path, mode='w') as f:
                            req = self.service.files().get_media(fileId=i['id'])
                            downloader = MediaIoBaseDownload(f, req)
                            while done is False:
                                status, done = downloader.next_chunk()
                                print('完了')
                    # 失敗時は再試行
                    except Exception:
                        print('失敗')
                        print('再試行します。')
            if page_token is None:
                break
