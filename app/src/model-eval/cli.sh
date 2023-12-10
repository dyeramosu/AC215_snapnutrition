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
