#!/bin/bash

set -e

export IMAGE_NAME="snapnutrition-app-frontend-react"

docker build -t $IMAGE_NAME -f Dockerfile .
docker run --rm --name $IMAGE_NAME -v "$(pwd)/:/app/" -p 3000:3000 $IMAGE_NAME