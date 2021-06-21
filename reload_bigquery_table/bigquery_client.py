from google.cloud import bigquery
from google.api_core.exceptions import NotFound
from google.auth.exceptions import DefaultCredentialsError
from pathlib import Path
from typing import Union

import gcp_logger
import json

logger = gcp_logger.get_logger()


class GoogleBigQueryClient:
    def __init__(self, keyfile=Path(__file__).parent / "keyfile.json"):
        # Try to initialize BigQuery Client, if not configured in environment look for keyfile.json.
        try:
            self.bigquery_client = bigquery.Client()
        except DefaultCredentialsError:
            self.bigquery_client = bigquery.Client.from_service_account_json(keyfile)

    @staticmethod
    def _load_bigquery_schema(schema_file: str):
        schema_dict = json.load(open(schema_file, "r"))
        schema = []
        for item in schema_dict["schema"]:
            schema.append(bigquery.SchemaField(item.get("name"), item.get("type")))
        return schema

    def delete_bigquery_table(self, bq_dataset_name: str, bq_table_name: str):
        try:
            self.bigquery_client.delete_table(table=f"{bq_dataset_name}.{bq_table_name}")
            logger.info(f'BigQuery table {bq_table_name} deleted')
        except NotFound as nf:
            logger.warning(f'BigQuery table {bq_table_name} NOT FOUND')

    def create_bigquery_table_from_gcs(self, bq_dataset_name: str, bq_table_name: str, gcs_bucket_name: str,
                                       gcs_blob_path: str, schema_file: Union[str, None] = "bigquery_schema.json",
                                       bq_max_bad_records: int = 1000):
        """
        Creates a bigquery table and loads data from Cloud Storage
        Parameters
        ----------
        bq_dataset_name : str
            name of dataset where table is located in
        bq_table_name : str
            name of table
        gcs_bucket_name : str
            name of bucket to load data from
        gcs_blob_path : str
            path within Cloud Storage Bucket to objects
        schema_file : str
            location of schema file
        bq_max_bad_records : int
            number of allowed bad records when loading data into table
        """

        bq_table_name = f'marjoland.{bq_dataset_name}.{bq_table_name}'
        if schema_file:
            schema = self._load_bigquery_schema(schema_file)
        else:
            schema = None

        job_config = bigquery.LoadJobConfig(
            schema=schema,
            autodetect=False,
            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
            max_bad_records=bq_max_bad_records
        )
        logger.debug(f"bq_table_name {bq_table_name}")
        load_job = self.bigquery_client.load_table_from_uri(
            source_uris=[f'gs://{gcs_bucket_name}/{gcs_blob_path}'],
            destination=bq_table_name,
            job_config=job_config,
        )

        load_job.result()  # Waits for the job to complete.

        destination_table = self.bigquery_client.get_table(bq_table_name)
        logger.info(f"Loaded {destination_table.num_rows} rows into {bq_table_name}")
