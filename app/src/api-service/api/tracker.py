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

        # Download file
        _, ext = os.path.splitext(source_path)
        if bool(ext):
            blob = bucket.get_blob(source_path)
            blob.download_to_filename(os.path.join(destination_path, os.path.basename(source_path)))
            return
        
        # Download directory
        for item in tf.io.gfile.glob(f"gs://{bucket_name}/{source_path}/*"):
            item = item.replace(f"gs://{bucket_name}/", "")
            _, ext = os.path.splitext(item)
            if bool(ext):
                blob = bucket.get_blob(item)
                blob.download_to_filename(os.path.join(destination_path, os.path.basename(item)))
            else:
                new_destination_path = os.path.join(destination_path, os.path.basename(item))
                if not os.path.exists(new_destination_path):
                    os.mkdir(new_destination_path)
                download_from_bucket(
                    item, 
                    new_destination_path, 
                    bucket_name, 
                    project_name
                )


def download_experiment_results(timestamp):
    """Get all experiment results"""

    results_file = 'model_eval/experiment_results.csv'
    local_results_file = os.path.join(
            local_experiments_path, os.path.basename(results_file)
        )
    
    file_timestamp = os.path.getmtime(local_results_file)

    if file_timestamp > timestamp:
        download_from_bucket(
            results_file,
            local_experiments_path,
            bucket_name,
            project_name
        )
        timestamp = file_timestamp
    
    return timestamp


def download_best_model():
    print("Download best model")
    try:
        experiments = pd.read_csv(local_experiments_path + "/experiment_results.csv")
        print("Shape:", experiments.shape)
        print(experiments.head())

        # Find the overall best model 
        best_model = experiments.iloc[0].to_dict()
        
        # Create a json file best_model.json
        with open(
            os.path.join(local_experiments_path, "best_model.json"), "w"
        ) as json_file:
            json_file.write(json.dumps(best_model))

        # Setup best model folder
        best_model_path = os.path.join(local_experiments_path, 'best_model')
        if not os.path.exists(best_model_path):
            os.mkdir(best_model_path)
        
        # Download model
        download_from_bucket(
            'model_eval/best_model',
            best_model_path,
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
            timestamp = download_experiment_results(self.timestamp)

            if timestamp > self.timestamp:
                # Download best model
                download_best_model()

                # Reset timestamp
                self.timestamp = timestamp