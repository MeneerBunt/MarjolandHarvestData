import os

from bigquery_client import GoogleBigQueryClient


def main(event, context):
    bigquery_dataset_name = os.getenv("BIGQUERY_DATASET_NAME")
    bigquery_table_name = os.getenv("BIGQUERY_TABLE_NAME")
    cloud_storage_bucket_name = os.getenv("GCS_BUCKET_NAME")
    bq_max_bad_records = int(os.getenv("BQ_MAX_BAD_RECORDS"))

    bq_client = GoogleBigQueryClient()

    bq_client.delete_bigquery_table(
        bq_dataset_name=bigquery_dataset_name,
        bq_table_name=bigquery_table_name
    )

    bq_client.create_bigquery_table_from_gcs(
        bq_dataset_name=bigquery_dataset_name,
        bq_table_name=bigquery_table_name,
        gcs_bucket_name=cloud_storage_bucket_name,
        gcs_blob_path="*.jsonl",
        bq_max_bad_records=bq_max_bad_records
    )
