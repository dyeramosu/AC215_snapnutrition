# Overview
The purpose of this model-eval container is as follows:

1. Evaluate a list of models that have already been trained
2. Create an evaluation summary called `experiment_results.csv` and store it in the `snapnutrition_data_bucket` GCS bucket within the `model_eval` folder
3. Find the best model and store it in the `best_model` folder within the `model_eval` folder in the GCS bucket

## Dependencies

This container depends on our `image_prep` container, `tfrecords_creation` containers, and our `model-train` or `model-sweeps` containers.  Our `image_prep` container process raw images from the Nutrition 5K dataset and our `tfrecords_creation` container creates TensorFlow Datasets, stores them in a Google Cloud Bucket, and also versions these records using Data Version Control [dvc](dvc.org).  See the tfrecord_creation container README.md for a more detailed description.  The `model-trainer`/`model-sweeps` containers are needed to create trained models that can be fetched from Weights & Biases. This container uses these TensorFlow Datasets to efficiently evaluate our models.

## Instructions:

*Adopted from the following GitHub Repository developed and provided by Shivas Javaram [https://github.com/dlops-io/model-training](https://github.com/dlops-io/model-training)*

### Setup GCP Credentials

Enable this container to have access to Storage buckets & Vertex AI(AI Platform) in GCP. 

#### Create a local **secrets** folder

It is important to note that we do not want any secure information in Git. So we will manage these files outside of the git folder. 

Folder Structure:
```
   |-model-sweeps
   |-secrets
```

#### Setup GCP Service Account

- Go to [GCP Console](https://console.cloud.google.com/home/dashboard), search for  "Service accounts" from the top search box. or go to: "IAM & Admins" > "Service accounts" from the top-left menu and create a new service account called "model-trainer". For "Service account permissions" select "Storage Admin", "AI Platform Admin", "Vertex AI Administrator".
- This will create a service account.
- On the right "Actions" column click the vertical ... and select "Manage keys". A prompt for Create private key for "model-trainer" will appear select "JSON" and click create. This will download a Private key json file to your computer. Copy this json file into the **secrets** folder. Rename the json file to `model-trainer.json`

### Create GCS Bucket

We need a bucket to store the packaged python files that we will use for training.

- Go to `https://console.cloud.google.com/storage/browser`
- Create a bucket `snapnutrition_data_bucket`

### Get WandB Account API Key

We want to track our model training runs using WandB. Get the API Key for WandB: 
- Login into [WandB](https://wandb.ai/home)
- Go to to [User settings](https://wandb.ai/settings)
- Scroll down to the `API keys` sections 
- Copy the key
- Set an environment variable using your terminal: `export WANDB_KEY=...` 
- Note: For Windows, set environment variable using Command Terminal `set WANDB_KEY=...`

### Review Build Files 

- Open & Review `model-eval` > `cli.py`. Ensure the global variables are correctly set before executing. 
- Open & Review `model-eval` > `cli.sh`. Ensure the global variables are correctly set before executing.
- Open & Review `model-eval` > `eval_list.yml`. Place all names of the runs you would like to evaluate in this YAML file. The `cli.py` script will skip through models that have already been evaluated, so no need to worry about removing names before executing. These names can be found in the Weights & Biases project page.  

### Run Container

#### Run `sh docker-shell.sh` or `docker-shell.bat`
Based on your OS, run the startup script to make building & running the container easy.

This is what your `docker-shell.sh` file will look like:
```
#!/bin/bash

set -e

export IMAGE_NAME=model-sweeps-cli
export BASE_DIR=$(pwd)
export SECRETS_DIR=$(pwd)/../secrets/
export GCS_BUCKET_NAME="snapnutrition_data_bucket"
export GCS_BUCKET_URI="gs://$GCS_BUCKET_NAME"
export GCP_PROJECT="csci-115-398800"

# Build the image based on the Dockerfile
docker build -t $IMAGE_NAME -f Dockerfile .
# M1/2 chip macs use this line
#docker build -t $IMAGE_NAME --platform=linux/arm64/v8 -f Dockerfile .

# Run Container
docker run --rm --name $IMAGE_NAME -ti \
-v "$BASE_DIR":/app \
-v "$SECRETS_DIR":/secrets \
-e GOOGLE_APPLICATION_CREDENTIALS=/secrets/model-training.json \
-e GCP_PROJECT=$GCP_PROJECT \
-e GCS_BUCKET_NAME=$GCS_BUCKET_NAME \
-e GCS_BUCKET_URI=$GCS_BUCKET_URI \
-e WANDB_KEY=$WANDB_KEY \
$IMAGE_NAME
```

- Make sure you are inside the `model-eval` folder and open a terminal at this location
- Run `sh docker-shell.sh` or `docker-shell.bat` for windows
- The `docker-shell` file assumes you have the `WANDB_KEY` as an environment variable and is passed into the container


#### Run `sh cli.sh`
- Open & Review `model-eval` > `cli.sh`
- `cli.sh` is a script file to make calling `cli.py` easier by maintaining all the parameters in the script
- Make any required changes to your `cli.sh`.

This is what your `cli.sh` file will look like:
```
# Set location of tfrecords test data 
export TFRECORDS_FOLDER="data/tf_records/224_by_224/"

# Set location of model evaluation folder to store 
# experiment results and best model
export MODEL_EVAL_FOLDER="model_eval/"

python3 cli.py \
 --wandb_key=$WANDB_KEY \
 --bucket=$GCS_BUCKET_NAME \
 --project=$GCP_PROJECT \
 --tfrecords_folder=$TFRECORDS_FOLDER \
 --model_eval_folder=$MODEL_EVAL_FOLDER
```


#### Inspect `experiment_results.csv`
- Upon completing `cli.sh`, `experiment_results.csv` will appear in your working directory. Open it to see results of all models evaluated.
- **Note:** `experiment_results.csv` is downloaded from the GCS bucket before being updated and then reloaded into the bucket. Therefore, it will accumulate all runs that have been evaluated to date. 
- Add more runs to `eval_list.yml` and rerun `cli.sh` if you wish. No need to exit and rebuild the Docker container.