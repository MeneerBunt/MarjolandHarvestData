import jsonlines
import os

from pathlib import Path
from xml_handler import XmlHandler
from google_cloud_storage_client import GoogleCloudStorageClient


def main(event, context):
    # Retrieve file from GCS
    input_filename = event.get("name")
    input_bucket_name = event.get("bucket")
    output_bucket_name = os.environ.get("OUTPUT_BUCKET_NAME")

    gcs_client = GoogleCloudStorageClient()

    local_filename = gcs_client.download_file_from_gcs(bucket_name=input_bucket_name, source_blob=input_filename)

    # Read file and parse to List[dict]
    xml_content_dict = XmlHandler.read_xml_file(file_path=local_filename)
    parsed_row_list = XmlHandler.parse_harvest_xml_to_json(content_dict=xml_content_dict)

    # Write file to jsonlines
    output_filename = Path(input_filename).stem + '.jsonl'

    local_output_file = Path("/tmp") / output_filename
    with jsonlines.open(local_output_file, mode="w") as writer:
        writer.write_all(parsed_row_list)

    # Upload file to GCS
    gcs_client.upload_file_to_gcs(bucket_name=output_bucket_name, destination_blob=Path(output_filename).name,
                                  source_filename=local_output_file, remove_local_file=True)
