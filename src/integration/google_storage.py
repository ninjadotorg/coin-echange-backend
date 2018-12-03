import os

from django.conf import settings
from google.cloud import storage
from google.cloud.storage import Blob

from common.decorators import raise_api_exception
from integration.exceptions import ExternalAPIException


bucket = None


@raise_api_exception(ExternalAPIException)
def upload_file(full_file_name: str, file):
    blob = Blob(full_file_name, get_bucket())
    blob.upload_from_file(file)

    return blob


def get_bucket():
    global bucket
    if not bucket:
        client = storage.Client.from_service_account_json(
            os.path.normpath(os.path.join(settings.DJANGO_ROOT, 'coin-exchange-storage.json')))
        bucket = client.get_bucket(settings.STORAGE_BUCKET)
    return bucket
