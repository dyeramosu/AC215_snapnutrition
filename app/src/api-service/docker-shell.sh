#!/bin/bash

# exit immediately if a command exits with a non-zero status
set -e

# Define some environment variables
export IMAGE_NAME="snapnutrition-app-api-service"
export BASE_DIR=$(pwd)
export SECRETS_DIR=$(pwd)/../../../secrets/
export PERSISTENT_DIR=$(pwd)/../../../persistent-folder/
export GCS_BUCKET_NAME="snapnutrition_data_bucket"
export GCP_PROJECT="csci-115-398800"

# Build the image based on the Dockerfile
docker build -t $IMAGE_NAME -f Dockerfile .
# M1/2 chip macs use this line
# docker build -t $IMAGE_NAME --platform=linux/arm64/v8 -f Dockerfile .

# Run the container
docker run --rm --name $IMAGE_NAME -ti \
-v "$BASE_DIR":/app \
-v "$SECRETS_DIR":/secrets \
-v "$PERSISTENT_DIR":/persistent \
-p 9000:9000 \
-e DEV=1 \
-e GOOGLE_APPLICATION_CREDENTIALS=/secrets/model-deployment.json \
-e GCS_BUCKET_NAME=$GCS_BUCKET_NAME \
-e GCP_PROJECT=$GCP_PROJECT \
$IMAGE_NAME
