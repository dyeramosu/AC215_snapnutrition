#!/bin/bash

set -e

export IMAGE_NAME=labels-processing-docker-image
export BASE_DIR=$(pwd)
export SECRETS_DIR=$(pwd)/../secrets/
export GCS_BUCKET_URI="gs://snapnutrition_data_bucket"
export GCP_PROJECT="csci-115-398800"
export GCP_REGION="us-central1"


# Build the image based on the Dockerfile
docker build -t $IMAGE_NAME -f data_versioning_control/Dockerfile .

# M1/2 chip macs use this line
# docker build -t $IMAGE_NAME --platform=linux/arm64/v8 -f data_versioning_control/Dockerfile .

sudo docker run --rm --name $IMAGE_NAME --privileged  -ti \
-v "$BASE_DIR":/app \
-v "$SECRETS_DIR":/secrets \
-v "/home/wschristina/.ssh/":/home/app/.ssh \
-e GOOGLE_APPLICATION_CREDENTIALS=/secrets/dvc-secrets.json \
-e GCP_PROJECT=$GCP_PROJECT \
-e GCP_REGION=$GCP_REGION \
-e GCS_BUCKET_URI=$GCS_BUCKET_URI \
$IMAGE_NAME
