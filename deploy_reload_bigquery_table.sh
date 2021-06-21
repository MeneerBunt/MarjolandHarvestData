gcloud pubsub topics delete bigquery_reload_table_topic
gcloud pubsub topics create bigquery_reload_table_topic

cp gcp_logger.py reload_bigquery_table/
cd reload_bigquery_table &&
  gcloud functions deploy reload_bigquery_table \
    --runtime python39 \
    --region europe-west3 \
    --trigger-topic bigquery_reload_table_topic \
    --set-env-vars BIGQUERY_DATASET_NAME=harvest_dataset,BIGQUERY_TABLE_NAME=harvest_data_table_production,GCS_BUCKET_NAME=json_store_marjoland,BQ_MAX_BAD_RECORDS=1000 \
    --entry-point main \
    --memory=256MB \
    --timeout=300 \
    --source="$(pwd)" &&
  rm gcp_logger.py

gcloud scheduler jobs delete bigquery_reload_table_job --quiet
gcloud scheduler jobs create pubsub bigquery_reload_table_job \
  --schedule "0 0 * * *" --topic bigquery_reload_table_topic \
  --time-zone "Etc/UTC" \
  --message-body "reload bigquery table"
