set "image_name=model-training-cli"
set "base_dir=%cd%"
set "secrets_dir=%cd%\..\..\..\secrets\"
set "gcs_bucket_name=snapnutrition_data_bucket"
set "gcs_bucket_uri=gs://%gcs_bucket_name%"
set "gcp_project=csci-115-398800"

REM build the image based on the dockerfile
docker build -t %image_name% -f C:\Users\wschr\PycharmProjects\AC215_snapnutrition\model-sweeps\Dockerfile .

REM run container
docker run --rm --name %image_name% -ti ^
-v %base_dir%:/app ^
-v %secrets_dir%:/secrets ^
-e GOOGLE_APPLICATION_CREDENTIALS=/secrets/model-trainer.json ^
-e GCP_PROJECT=%gcp_project% ^
-e GCS_BUCKET_NAME=%gcs_bucket_name% ^
-e GCS_BUCKET_URI=%gcs_bucket_uri% ^
-e WANDB_KEY=%wandb_key% ^
%image_name%