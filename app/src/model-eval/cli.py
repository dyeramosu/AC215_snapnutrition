import os
import math
import argparse
import yaml
import json
import shutil
import glob
import numpy as np
import pandas as pd
from google.cloud import storage

# sklearn
from sklearn.metrics import mean_absolute_error, mean_squared_error

# TensorFlow
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' # silence tf info, error, warning messages
import tensorflow as tf
from tensorflow.python.keras.utils.layer_utils import count_params

print(f'Tensorflow Version: {tf.__version__}')
print("Eager Execution Enabled:", tf.executing_eagerly())
strategy = tf.distribute.MirroredStrategy()
print("Number of Replicas:", strategy.num_replicas_in_sync)
devices = tf.config.experimental.get_visible_devices()
print("Devices:", devices)
print(tf.config.experimental.list_logical_devices('GPU'))
print("GPU Available: ", tf.config.list_physical_devices('GPU'))
print("All Physical Devices", tf.config.list_physical_devices())

# Weights & Biases
import wandb


# Parse command line arguments
parser = argparse.ArgumentParser(
    description='Evaluate a list of models given a YAML file.'
)
parser.add_argument(
    '-w',
    '--wandb_key',
    required=True,
    type=str, 
    help="Weights and Biases API Key"
)
parser.add_argument(
    '-b',
    '--bucket',
    required=True,
    type=str, 
    help="GCS bucket name"
)
parser.add_argument(
    '-p',
    '--project',
    required=True,
    type=str, 
    help="GCP project name"
)
parser.add_argument(
    '-tf',
    '--tfrecords_folder',
    required=True,
    type=str, 
    help="TF records folder path in GCS bucket"
)
parser.add_argument(
    '-me',
    '--model_eval_folder',
    required=True,
    type=str, 
    help="Model eval folder path in GCS bucket"
)
args = parser.parse_args()


# Define Weights & Biases variables
ENTITY = "snap-nutrition"
PROJECT = "snapnutrition-training-vertex-ai"


# Define dataset globals
global image_size, image_shape, num_classes
image_shape = [224, 224, 3]
image_size = [math.prod(tuple(image_shape))]
num_classes = 5


# Helper for uploading to GCS bucket
def upload_to_bucket(src_path, dest_path, bucket_name, project_name):
        storage_client = storage.Client(project=project_name)
        bucket = storage_client.bucket(bucket_name)
        if os.path.isfile(src_path):
            blob = bucket.blob(os.path.join(dest_path, os.path.basename(src_path)))
            blob.upload_from_filename(src_path)
            return
        for item in glob.glob(src_path + '/*'):
            if os.path.isfile(item):
                blob = bucket.blob(os.path.join(dest_path, os.path.basename(item)))
                blob.upload_from_filename(item)
            else:
                upload_to_bucket(
                    item, 
                    os.path.join(dest_path, os.path.basename(item)), 
                    bucket_name, 
                    project_name
                )


# Upload best model to GCS bucket 
def upload_best_model(bucket_name, project_name, model_eval_folder):
    best_model_path = os.path.join(model_eval_folder, "best_model")
    print(f"Uploading best model to '{os.path.join(bucket_name, best_model_path)}'")

    # Instantiate GCS client
    storage_client = storage.Client(project=project_name)
    bucket = storage_client.bucket(bucket_name)

    # Delete previous model
    blobs = bucket.list_blobs(prefix=best_model_path)
    for blob in blobs:
        blob.delete() 

    # Upload model
    upload_to_bucket("model", best_model_path, bucket_name, project_name)
    print('Upload complete') 
    

# Upload 'experiments.csv' to GCS bucket 
def upload_experiment_results(bucket_name, project_name, model_eval_folder):
    print(f"Uploading experiment results to '{os.path.join(bucket_name, model_eval_folder)}'")

    # Upload model
    upload_to_bucket("experiment_results.csv", model_eval_folder, bucket_name, project_name)
    print('Upload complete')  


# Download tfrecords files from GCS bucket
def download_tfrecords(bucket_name, project_name, tfrecords_folder):
    print(f"Downloading tfrecords files from '{os.path.join(bucket_name, tfrecords_folder)}'")

    # Create download folder
    download_destination = 'data'
    os.makedirs(download_destination, exist_ok=True)

    # Instantiate GCS client
    client = storage.Client(project=project_name)

    # Download test tfrecords locally
    blobs = client.list_blobs(bucket_name, prefix=tfrecords_folder)
    for blob in blobs:
        # Exclude parent folder
        if blob.name.endswith("/"):
            continue

        # Exclude train and val records
        blob_path = blob.name.split('/') 
        if blob_path[-1].startswith("train") or blob_path[-1].startswith("val"):
            continue

        # Skip download if file already exists
        if os.path.exists(os.path.join(download_destination, blob_path[-1])):
            print(f"'{blob_path[-1]}' already exists in '{download_destination}/'")
            continue

        print(f"Downloading: '{blob_path[-1]}'")
        blob.download_to_filename(
            os.path.join(download_destination, os.path.basename(blob.name))
        )
    print('Download complete')
    

# Download experiment results from GCS bucket
def download_experiment_results(bucket_name, project_name, model_eval_folder):
    print(f"Downloading experiment results from '{os.path.join(bucket_name, model_eval_folder)}'")

    # Instantiate GCS client
    client = storage.Client(project=project_name)

    # Download experiment results locally
    blobs = client.list_blobs(bucket_name, prefix=model_eval_folder)
    for blob in blobs:
        if blob.name.endswith(".csv"):
            blob_path = blob.name.split('/') 
            print(f"Downloading: '{blob_path[-1]}'")
            blob.download_to_filename(
                os.path.join(os.getcwd(), os.path.basename(blob.name))
            )
    print('Download complete')
    

# Parse a single image and label
def parse_tfrecord_example(example):
    # Read TF Records
    feature_description = {
        'image': tf.io.FixedLenFeature([], tf.string),
        'label': tf.io.FixedLenFeature([5], tf.float32, default_value=[0.0, 0.0, 0.0, 0.0, 0.0])
    }
    
    parsed_example = tf.io.parse_single_example(example, feature_description)

    # Access global variables
    global image_size, image_shape

    # Image
    image = tf.io.decode_raw(parsed_example['image'], tf.float32)
    image.set_shape(image_size)
    image = tf.reshape(image, image_shape)
    
    # Label
    label = parsed_example['label']

    return image, label


# Normalize pixels
def normalize(image, label):
    image = image/255
    return image, label


# Load train and validation data from tfrecords files
def load_tfrecords(
        tfrecords_directory,
        batch_size,
        normalize_data=False
    ):
    # Read the tfrecord files
    test_tfrecord_files = tf.data.Dataset.list_files(tfrecords_directory+'/test*')

    # Test data
    test_data = test_tfrecord_files.flat_map(tf.data.TFRecordDataset)
    test_data = test_data.map(parse_tfrecord_example, num_parallel_calls=tf.data.AUTOTUNE)
    if normalize_data:
        test_data = test_data.map(normalize, num_parallel_calls=tf.data.AUTOTUNE)
    test_data = test_data.batch(batch_size)
    test_data = test_data.prefetch(buffer_size=tf.data.AUTOTUNE)

    print("test_data",test_data)

    return test_data


# Fetch data
download_tfrecords(args.bucket, args.project, args.tfrecords_folder)
test_data = load_tfrecords(
    'data',
    128,
    normalize_data=False
)


# Fetch experment results
download_experiment_results(args.bucket, args.project, args.model_eval_folder)
experiments_df = pd.read_csv("experiment_results.csv")
already_evaluated = experiments_df['model_name'].tolist()


# Read YAML file with list of models to evaluate
with open('eval_list.yml', 'r') as file:
    eval_list = yaml.safe_load(file)
eval_list = eval_list['model_names']


# Login to Weights & Biases and get runs
wandb.login(key=args.wandb_key)
api = wandb.Api()
runs = api.runs(f"{ENTITY}/{PROJECT}")


# Evaluate runs in the eval list 
# Skip those that have already been evaluated
for run in runs:
    if run.name not in eval_list:
        continue
    if run.name in already_evaluated:
        print(f"Skipping {run.name}... \n>>> Already evaluated")
        continue
    print(f"Evaluating: {run.name}")

    # Download model from WANDB
    for artifact in run.logged_artifacts():
        # Find 'model' artifact
        if artifact.type == "model":
            model_artifact = artifact # This stores the latest model
    model_dir = "model"
    shutil.rmtree(model_dir, ignore_errors=True, onerror=None)
    os.makedirs(model_dir, exist_ok=True)
    model_dir = model_artifact.download(root=os.path.join(os.getcwd(), model_dir))

    # Load model
    prediction_model = tf.keras.models.load_model(model_dir)
    model_size = model_artifact.size / 1024**2
    model_config = json.loads(run.json_config)
    print(f"Model size: {model_size:.02f} MB")
    print(prediction_model.summary())

    # Make predictions
    predictions = []
    truth = []
    for batch in test_data:
        images, labels = batch
        batch_predictions = prediction_model.predict(images)
        predictions.extend(batch_predictions)
        truth.extend(labels)
    predictions = np.stack(predictions, axis=0)
    truth = np.stack(truth, axis=0)

    # Calculate model performance
    MAE = mean_absolute_error(truth, predictions)
    MSE = mean_squared_error(truth, predictions)
    RMSE = np.sqrt(MSE)
    print(f"\nMAE: {MAE:.02f}")
    print(f"MSE: {MSE:.02f}")
    print(f"RMSE: {RMSE:.02f}\n")

    # Create results dataframe
    results = {
        'actual_calories': truth[:, 0], 
        'pred_calories': predictions[:, 0], 
        'actual_mass': truth[:, 1], 
        'pred_mass': predictions[:, 1],
        'actual_fat': truth[:, 2], 
        'pred_fat': predictions[:, 2], 
        'actual_carb': truth[:, 3], 
        'pred_carb': predictions[:, 3],
        'actual_protein': truth[:, 4], 
        'pred_protein': predictions[:,4]
    }
    results_df = pd.DataFrame(data=results)
    results_df['calorie_difference'] = results_df.apply(
        lambda x: x['actual_calories'] - x['pred_calories'], 
        axis=1
    )
    results_df['mass_difference'] = results_df.apply(
        lambda x: x['actual_mass'] - x['pred_mass'], 
        axis=1
    )
    results_df['fat_difference'] = results_df.apply(
        lambda x: x['actual_fat'] - x['pred_fat'], 
        axis=1
    )
    results_df['carb_difference'] = results_df.apply(
        lambda x: x['actual_carb'] - x['pred_carb'], 
        axis=1
    )
    results_df['protein_difference'] = results_df.apply(
        lambda x: x['actual_protein']-x['pred_protein'], 
        axis=1
    )

    # Calculate results
    avg_calories_off =  results_df['calorie_difference'].abs().mean()
    avg_mass_off = results_df['mass_difference'].abs().mean()
    avg_fat_off = results_df['fat_difference'].abs().mean()
    avg_carb_off = results_df['carb_difference'].abs().mean()
    avg_protein_off = results_df['protein_difference'].abs().mean()

    min_calories_off = results_df['calorie_difference'].min()
    min_mass_off = results_df['mass_difference'].min()
    min_fat_off = results_df['fat_difference'].min()
    min_carb_off = results_df['carb_difference'].min()
    min_protein_off = results_df['protein_difference'].min()

    max_calories_off =  results_df['calorie_difference'].max()
    max_mass_off = results_df['mass_difference'].max()
    max_fat_off = results_df['fat_difference'].max()
    max_carb_off = results_df['carb_difference'].max()
    max_protein_off = results_df['protein_difference'].max()

    print(f"average calories off: {avg_calories_off:.02f} cal")
    print(f"average mass off: {avg_mass_off:.02f} grams")
    print(f"average fat off: {avg_fat_off:.02f} grams")
    print(f"average carb off: {avg_carb_off:.02f} grams")
    print(f"average protein off: {avg_protein_off:.02f} grams\n")

    print(f"min calories off: {min_calories_off:.02f} cal")
    print(f"min mass off: {min_mass_off:.02f} grams")
    print(f"min fat off: {min_fat_off:.02f} grams")
    print(f"min carb off: {min_carb_off:.02f} grams")
    print(f"min protein off: {min_protein_off:.02f} grams\n")

    print(f"max calories off: {max_calories_off:.02f} cal")
    print(f"max mass off: {max_mass_off:.02f} grams")
    print(f"max fat off: {max_fat_off:.02f} grams")
    print(f"max carb off: {max_carb_off:.02f} grams")
    print(f"max protein off: {max_protein_off:.02f} grams\n")

    # Build model summary dataframe
    model_metrics = {
        'model_name': run.name,
        'MAE': MAE,
        'MSE': MSE,
        'RMSE': RMSE,
        'avg_calories_off': avg_calories_off,
        'avg_mass_off': avg_mass_off,
        'avg_fat_off': avg_fat_off,
        'avg_carb_off': avg_carb_off,
        'avg_protein_off': avg_protein_off,
        'min_calories_off': min_calories_off,
        'min_mass_off': min_mass_off,
        'min_fat_off': min_fat_off,
        'min_carb_off': min_carb_off,
        'min_protein_off': min_protein_off,
        'max_calories_off': max_calories_off,
        'max_mass_off': max_mass_off,
        'max_fat_off': max_fat_off,
        'max_carb_off': max_carb_off,
        'max_protein_off': max_protein_off,
        'trainable_parameters': count_params(prediction_model.trainable_weights),
        'nontrainable_parameters': count_params(prediction_model.non_trainable_weights),
        'model_size': f"{model_size:.02f} MB",
        'execution_time': model_config["execution_time"]["value"],
        'input_shape': [model_config["input_shape"]["value"]],
        'loss': model_config["loss"]["value"],
        'epochs': run.summary["best_epoch"],
        'optimizer': model_config["optimizer"]["value"],
        'batch_size': model_config["batch_size"]["value"],
        'learning_rate': model_config["learning_rate"]["value"],
    }

    # Create metrics dataframe 
    metrics_df = pd.DataFrame(data=model_metrics)

    # Check for best model
    if float(metrics_df['MAE'].iloc[0]) < float(experiments_df['MAE'].iloc[0]):
        print('New Best Model!!!')
        upload_best_model(args.bucket, args.project, args.model_eval_folder)

    # Concatenate to experiments dataframe
    experiments_df = pd.concat([experiments_df, metrics_df], ignore_index=True)


# Overwrite experiment_results.csv and reorder according to best MAE
experiments_df = experiments_df.sort_values(by='MAE', ascending=True)
experiments_df.to_csv('experiment_results.csv', index=False)

# Upload metrics to GCS bucket
upload_experiment_results(args.bucket, args.project, args.model_eval_folder)