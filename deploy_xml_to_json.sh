cp gcp_logger.py convert_xml_to_json/
cd convert_xml_to_json &&
  gcloud functions deploy convert_xml_to_json \
    --runtime python39 \
    --region europe-west3 \
    --trigger-resource marjoland-harvest-data-production \
    --trigger-event google.storage.object.finalize \
    --set-env-vars OUTPUT_BUCKET_NAME=json_store_marjoland \
    --entry-point main \
    --memory=256MB \
    --timeout=300 \
    --source="$(pwd)" &&
  rm gcp_logger.py
