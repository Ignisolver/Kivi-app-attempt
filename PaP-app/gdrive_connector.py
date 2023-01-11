import io
from datetime import datetime

from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

from app.app.google import Create_Service


class GDriveConnector:
    CLIENT_SECRET_FILE = "client_secret.json"
    API_NAME = 'drive'
    API_VERSION = 'v3'
    SCOPES = ["https://www.googleapis.com/auth/drive"]

    def __init__(self):
        self.service = Create_Service(self.CLIENT_SECRET_FILE, self.API_NAME, self.API_VERSION, self.SCOPES)

    def create_folder(self, name, parents=[]):
        file_metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': parents
        }
        file = self.service.files().create(body=file_metadata,
                                           fields='id').execute()
        return file['id']

    def get_id(self, name):
        page_token = None
        while True:
            response = self.service.files().list(q=f"name='{name}'",
                                                 spaces='drive',
                                                 fields='nextPageToken, files(id, name)',
                                                 pageToken=page_token).execute()
            for file in response.get('files', []):
                return file.get('id')
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break

    def upload_file(self, name, src, parents=[], mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'):
        file_metadata = {
            'name': name,
            'mimeType': mimeType,
            'parents': parents
        }
        media = MediaFileUpload(src,
                                mimetype=mimeType,
                                resumable=True)
        file = self.service.files().create(body=file_metadata,
                                           media_body=media,
                                           fields='id').execute()
        return file['id']

    def update_file(self, file_id, src, mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'):
        media = MediaFileUpload(src,
                                mimetype=mimeType,
                                resumable=True)
        file = self.service.files().update(fileId=file_id,
                                           media_body=media).execute()
        return file['id']

    def download_xlsx_file(self, file_id, dest_file):

        bytedata = self.service.files().export_media(fileId=file_id,
                                                     mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                                                     ).execute()

        with open(dest_file, "wb") as f:
            f.write(bytedata)
            f.close()

    def list_directory(self, id):
        query = f"parents = '{id}'"
        response = self.service.files().list(q=query).execute()
        files = response.get('files')
        nextPageToken = response.get('nextPageToken')
        while nextPageToken:
            response = self.service.files().list(q=query).execute()
            files.extend(response.get('files'))
            nextPageToken = response.get('nextPageToken')

        return files

    def copy_file(self, id, name, parents, mimeType='application/vnd.google-apps.spreadsheet'):
        file_metadata = {
            'name': name,
            'mimeType': mimeType,
            'parents': parents
        }

        self.service.files().copy(
            fileId=id,
            body=file_metadata
        ).execute()

    def backup_folder(self, folder_id, name):
        files = self.list_directory(folder_id)
        backup_folder_id = self.get_id("Backup")
        time = datetime.now().strftime('%Y-%m-%d;%H.%M.%S')
        folder_id = self.create_folder(f"{name}-{time}", parents=[backup_folder_id])
        for file in files:
            self.copy_file(id=file['id'], name=f"{file['name']}-{time}", parents=[folder_id], mimeType=file['mimeType'])
