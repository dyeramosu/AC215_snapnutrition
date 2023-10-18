
# List of prebuilt containers for training
# https://cloud.google.com/vertex-ai/docs/training/pre-built-containers

export UUID=$(openssl rand -hex 6)
export DISPLAY_NAME="snapnutrition_training_job_$UUID"
export MACHINE_TYPE="n1-standard-4"
export REPLICA_COUNT=1
export PYTHON_PACKAGE_URI=$GCS_BUCKET_URI/trainer_package/snapnutrition-trainer.tar.gz
export PYTHON_MODULE="trainer.task"
export GCP_REGION="us-central1" # Adjust region based on you approved quotas for GPUs

# Set location of tfrecords train/val data 
export TFRECORDS_FOLDER="data/tf_records/180_by_180/"

# Set location to upload trained model weights
export MODELS_FOLDER="models/"

# Set trainer.task command arguments
export CMDARGS="--wandb_key=$WANDB_KEY,--bucket=$GCS_BUCKET_NAME,--project=$GCP_PROJECT,--tfrecords_folder=$TFRECORDS_FOLDER,--models_folder=$MODELS_FOLDER"

# Run training with GPU
# export EXECUTOR_IMAGE_URI="us-docker.pkg.dev/vertex-ai/training/tf-gpu.2-12.py310:latest"
# export ACCELERATOR_TYPE="NVIDIA_TESLA_T4"
# export ACCELERATOR_COUNT=1
# gcloud ai custom-jobs create \
#  --region=$GCP_REGION \
#  --display-name=$DISPLAY_NAME \
#  --python-package-uris=$PYTHON_PACKAGE_URI \
#  --worker-pool-spec=machine-type=$MACHINE_TYPE,replica-count=$REPLICA_COUNT,accelerator-type=$ACCELERATOR_TYPE,accelerator-count=$ACCELERATOR_COUNT,executor-image-uri=$EXECUTOR_IMAGE_URI,python-module=$PYTHON_MODULE \
#  --args=$CMDARGS


# Run training with CPU
 export EXECUTOR_IMAGE_URI="us-docker.pkg.dev/vertex-ai/training/tf-cpu.2-12.py310:latest"
 gcloud ai custom-jobs create \
   --region=$GCP_REGION \
   --display-name=$DISPLAY_NAME \
   --python-package-uris=$PYTHON_PACKAGE_URI \
   --worker-pool-spec=machine-type=$MACHINE_TYPE,replica-count=$REPLICA_COUNT,executor-image-uri=$EXECUTOR_IMAGE_URI,python-module=$PYTHON_MODULE \
   --args=$CMDARGS