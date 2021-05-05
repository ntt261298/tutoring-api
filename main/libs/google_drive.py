import httplib2
import logging
from io import BytesIO

from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient import discovery, errors as google_errors
from googleapiclient.http import MediaIoBaseUpload, HttpError

from config import config
from main import errors


class GoogleDriveEngine:
    def __init__(self, http=None):
        if http is None:
            credentials = ServiceAccountCredentials.from_json_keyfile_name(
                'credentials/google_client_secret.json',
                'https://www.googleapis.com/auth/drive')
            http = credentials.authorize(httplib2.Http(timeout=config.REQUEST_DEADLINE))
        service = discovery.build('drive', 'v3', http=http, cache_discovery=False)
        self.__service = service
        self.__http = http

    def upload(self, file_, filename, content_type):
        """
        create a file on google drive with the file provided
        :param file_: file-like object (supports read() method).
        :param filename: name of the file.
        :param content_type: mime type likes text/txt, image/png, ...
        :return: file meta data
        """
        # IMPORTANT: move the cursor to the begin of the file
        file_.seek(0, 0)
        file_metadata = {
            'name': filename,
            'mimeType': content_type,
        }
        media = MediaIoBaseUpload(
            file_,
            mimetype=content_type,
            chunksize=1024 * 1024,
            resumable=True)

        data = GoogleDriveEngine._execute(self.__service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, thumbnailLink'
        ))
        if data is None:
            raise errors.BadRequest()
        # Rename file to original filename because file uploaded to google will have an extra file extension
        self._rename_file(data.get('id'), filename)
        # Share file
        self._share_file_public_readonly(data.get('id'))
        return data['id'], _get_shared_link(data['id']), _get_embed_link(data['id'])

    def download(self, file_id):
        """
        Download a file
        :param file_id:
        :return: a tuple contains a file-like object, filename, content_type
        """
        # Get the file name
        file_ = GoogleDriveEngine._execute(self.__service.files().get(
            fileId=file_id,
            fields="name"
        ))
        if not file_:
            return None, None, None
        content = GoogleDriveEngine._execute(
            self.__service.files().export(
                fileId=file_id,
            )
        )
        filename = file_.get('name', '')
        return BytesIO(content), filename

    def delete(self, file_id):
        """
        Delete a file
        :param file_id:
        :return:
        """
        return GoogleDriveEngine._execute(self.__service.files().delete(fileId=file_id))

    def get_filename(self, file_id):
        """
        Get file metadata
        :param file_id:
        :return: name, mimeType
        """
        file_ = GoogleDriveEngine._execute(self.__service.files().get(
            fileId=file_id,
            fields="name"
        ))
        if not file_:
            return None, None
        return file_.get('name')

    def _share_file_public(self, file_id):
        public_permission = {
            'allowFileDiscovery': False,
            'type': 'anyone',
            'role': 'writer'
        }
        return GoogleDriveEngine._execute(self.__service.permissions().create(
            fileId=file_id, body=public_permission
        ))

    def _share_file_public_readonly(self, file_id):
        """
        share a file with other user
        :param file_id:
        :return: google drive permission response
        """
        # create file permission
        public_permission = {
            'allowFileDiscovery': False,
            'type': 'anyone',
            'role': 'reader'
        }
        return GoogleDriveEngine._execute(self.__service.permissions().create(
            fileId=file_id, body=public_permission
        ))

    def _rename_file(self, file_id, new_name):
        """
        rename file to new_name
        :param file_id:
        :param new_name:
        :return:
        """
        return GoogleDriveEngine._execute(self.__service.files().update(
            fileId=file_id,
            body={'name': new_name}
        ))

    @staticmethod
    def _execute(request):
        """
        Wrapping the google execution into a handling exception
        :param request:
        :return:
        """
        try:
            return request.execute()
        except HttpError as err:
            if err.resp.status == 404:
                raise errors.BadRequest()
        except google_errors.Error:
            logging.exception('Google Drive Api exception')
            raise errors.BadRequest()


def _get_shared_link(file_id):
    return 'https://docs.google.com/spreadsheets/d/{}'.format(file_id)


def _get_embed_link(file_id):
    return 'https://docs.google.com/spreadsheets/d/{}'.format(file_id)
