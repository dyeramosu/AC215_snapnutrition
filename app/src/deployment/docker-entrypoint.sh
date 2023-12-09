#!/bin/bash

echo "Container is running!!!"

# Authenticate gcloud using service account
gcloud auth activate-service-account --key-file $GOOGLE_APPLICATION_CREDENTIALS
# Set GCP Project Details
gcloud config set project $GCP_PROJECT
# Configure GCR
gcloud auth configure-docker gcr.io -q

/bin/bash
#CMD ["ansible-playbook", "deploy-k8s-cluster.yml", "-i", "inventory.yml", "--extra-vars", "cluster_state=present"]
gcloud container clusters create snapnutrition-app-cluster --machine-type=n2d-standard-2 --num-nodes=1 --service-account=deployment-russell@csci-115-398800.iam.gserviceaccount.com --zone=us-central1-a
ansible-playbook deploy-k8s-cluster.yml -i inventory.yml --extra-vars cluster_state=present