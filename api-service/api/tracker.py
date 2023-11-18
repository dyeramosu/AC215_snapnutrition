import os
import traceback
import asyncio
from glob import glob
import json
import pandas as pd

import tensorflow as tf
from google.cloud import storage


bucket_name = os.environ["GCS_BUCKET_NAME"]
project_name = os.environ["GCP_PROJECT"]
local_experiments_path = "/persistent/experiments"

# Setup experiments folder
if not os.path.exists(local_experiments_path):
    os.mkdir(local_experiments_path)


def download_from_bucket(
        source_path, # remove 'gs://<bucket_name>/' from path
        destination_path, 
        bucket_name, 
        project_name
    ):
        """Downloads a file or directory from a GCS bucket"""    
        storage_client = storage.Client(project=project_name)
        bucket = storage_client.bucket(bucket_name)
        if os.path.isfile(source_path):
            blob = bucket.blob(source_path)
            blob.download_to_filename(os.path.join(destination_path, os.path.basename(source_path)))
            return
        for item in glob(source_path + '/*'):
            if os.path.isfile(item):
                blob = bucket.blob(item)
                blob.download_to_filename(os.path.join(destination_path, os.path.basename(item)))
            else:
                if not os.path.exists(os.path.join(destination_path, item)):
                    os.mkdir(os.path.join(destination_path, item))
                download_from_bucket(
                    item, 
                    os.path.join(destination_path, item), 
                    bucket_name, 
                    project_name
                )


def download_experiment_results():
    """Get all experiment results"""

    timestamp = 0

    results_file = 'model_eval/experiment_results.csv'
    local_results_file = os.path.join(
            local_experiments_path, os.path.basename(results_file)
        )
    
    download_from_bucket(
        results_file,
        local_experiments_path,
        bucket_name,
        project_name
    )
    
    file_timestamp = os.path.getmtime(local_results_file)
    if file_timestamp > timestamp:
        timestamp = file_timestamp
    
    return timestamp


def download_best_model():
    print("Download best model")
    try:
        experiments = pd.read_csv(local_experiments_path + "/experiment_results.csv")
        print("Shape:", experiments.shape)
        print(experiments.head())

        # Find the overall best model across users
        best_model = experiments.iloc[0].to_dict()
        # Create a json file best_model.json
        with open(
            os.path.join(local_experiments_path, "best_model.json"), "w"
        ) as json_file:
            json_file.write(json.dumps(best_model))

        # Download model
        download_from_bucket(
            'model_eval/best_model',
            os.path.join(local_experiments_path, 'best_model'),
            bucket_name,
            project_name
        )       

    except:
        print("Error in download_best_model")
        traceback.print_exc()


class TrackerService:
    def __init__(self):
        self.timestamp = 0

    async def track(self):
        while True:
            await asyncio.sleep(60)
            print("Tracking experiments...")

            # Download new model metrics
            timestamp = download_experiment_results()

            if timestamp > self.timestamp:
                # Download best model
                download_best_model()