import os
from google.cloud import storage


# Upload a tensorflow model to GCS bucket 
def upload_model_weights(model, bucket_name, project_name, models_folder):
    print(f'Uploading model weights to {bucket_name}')

    # Create upload folder
    upload_source = 'uploads'
    os.makedirs(upload_source, exist_ok=True)

    # Save model weights
    file_name = f'{model.name}.h5'
    model.save_weights(os.path.join(upload_source, file_name))

    # Instantiate GCS client
    storage_client = storage.Client(project=project_name)
    bucket = storage_client.bucket(bucket_name)

    # Upload model
    blob = bucket.blob(os.path.join(models_folder, file_name))
    generation_match_precondition = 0
    blob.upload_from_filename(
        os.path.join(os.getcwd(), upload_source, file_name), 
        if_generation_match=generation_match_precondition
    )
    print('Upload complete')    


# Download tfrecords files from a GCS bucket
def download_tfrecords(bucket_name, project_name, tfrecords_folder):
    print(f'Downloading tfrecords files from {bucket_name}')

    # Create download folder
    download_destination = 'downloads'
    os.makedirs(download_destination, exist_ok=True)

    # Instantiate GCS client
    client = storage.Client(project=project_name)

    # Download tfrecords locally
    blobs = client.list_blobs(bucket_name, prefix=tfrecords_folder)
    for blob in blobs:
        if blob.name.endswith("/"):
            continue
        print(f'Downloading: {blob.name}')
        blob.download_to_filename(
            os.path.join(download_destination, os.path.basename(blob.name))
        )
    print('Download complete')