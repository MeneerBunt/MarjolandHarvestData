import os
from google.cloud import storage
from pathlib import Path
from google.auth.exceptions import DefaultCredentialsError


class GoogleCloudStorageClient:
    def __init__(self, keyfile=Path(__file__).parent / "keyfile.json"):

        # Try to initialize GCS Client, if not configured in environment look for keyfile.json.
        try:
            self.storage_client = storage.Client()
        except DefaultCredentialsError:
            self.storage_client = storage.Client.from_service_account_json(keyfile)

    def download_file_from_gcs(self, bucket_name: str, source_blob: str, destination_filename: str = None):
        """
        Parameters
        ----------
        bucket_name : str
            name of the bucket to get the object from
        source_blob : str
            path to the object relative to the object
        destination_filename : str, optional
            local filepath to save object to. If None /tmp/{source_filename} is used

        Returns
        -------
        str
            destination filename where file is saved
        """

        bucket = self.storage_client.bucket(bucket_name)
        blob = bucket.blob(source_blob)
        if not destination_filename:
            destination_filename = Path("/tmp") / source_blob

        blob.download_to_filename(destination_filename)
        print(f"file downloaded from {bucket_name} - {source_blob} to {destination_filename}")
        return destination_filename

    def upload_file_to_gcs(self, bucket_name: str, destination_blob: str, source_filename: str,
                           remove_local_file: bool = False):
        """
        Parameters
        ----------
        bucket_name : str
            name of bucket to upload object to
        destination_blob : str
            name/path to assign to object relative to bucket
        source_filename : str
            path to file to upload to bucket
        remove_local_file : bool
            boolean to remove file from local machine after uploading
        """

        bucket = self.storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob)
        blob.upload_from_filename(source_filename)
        print(f"file uploaded to {bucket_name} - {destination_blob} from {source_filename}")
        if remove_local_file:
            os.remove(source_filename)
            print(f"removed file {source_filename}")
