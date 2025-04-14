from google.cloud import bigquery
import os

def get_bq_client():
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "../secret/gcp_credentials.json"
    return bigquery.Client()

