"""
Module that contains the command line app.

Typical usage example from command line:
        python cli.py --upload
        python cli.py --deploy
        python cli.py --predict
"""

import os
import argparse
from glob import glob
import numpy as np
import base64
from google.cloud import storage
from google.cloud import aiplatform
import tensorflow as tf

## W&B
import wandb

# Global variables
GCP_PROJECT = os.environ["GCP_PROJECT"]
GCS_MODELS_BUCKET_NAME = os.environ["GCS_MODELS_BUCKET_NAME"]
BEST_MODEL = "distilled_student:v0"
ARTIFACT_URI = f"gs://{GCS_MODELS_BUCKET_NAME}/{BEST_MODEL}"
ARTIFACT_WB = "snap-nutrition/snap-nutrition/distilled_student:v0"
SERVING_CONTAINER_IMAGE_URI = "us-docker.pkg.dev/vertex-ai/prediction/tf2-cpu.2-12:latest"
MODEL_ENDPOINT = "projects/551792351994/locations/us-central1/endpoints/1274186642034262016"
IMAGE_SIZE = (224, 224)

def main(args=None):
    if args.upload:
        print("Upload model to GCS")

        storage_client = storage.Client(project=GCP_PROJECT)
        bucket = storage_client.get_bucket(GCS_MODELS_BUCKET_NAME)

        # Use this code if you want to pull your model directly from WandB
        WANDB_KEY = os.environ["WANDB_KEY"]
        # Login into wandb
        wandb.login(key=WANDB_KEY)

        # Download model artifact from wandb
        run = wandb.init()
        artifact = run.use_artifact(ARTIFACT_WB, type='model')
        artifact_dir = artifact.download()

        print("artifact_dir", artifact_dir)

        # Load model
        prediction_model = tf.keras.models.load_model(artifact_dir)
        print(prediction_model.summary())

        # Preprocess Image
        def preprocess_image(bytes_input):
            decoded = tf.io.decode_jpeg(bytes_input, channels=3)
            decoded = tf.image.convert_image_dtype(decoded, tf.float32)
            resized = tf.image.resize(decoded, size=IMAGE_SIZE)
            return resized

        @tf.function(input_signature=[tf.TensorSpec([None], tf.string)])
        def preprocess_function(bytes_inputs):
            decoded_images = tf.map_fn(
                preprocess_image, bytes_inputs, dtype=tf.float32, back_prop=False
            )
            return {"model_input": decoded_images}

        @tf.function(input_signature=[tf.TensorSpec([None], tf.string)])
        def serving_function(bytes_inputs):
            images = preprocess_function(bytes_inputs)
            results = model_call(**images)
            return results

        model_call = tf.function(prediction_model.call).get_concrete_function(
            [
                tf.TensorSpec(
                    shape=[None, 224, 224, 3], dtype=tf.float32, name="model_input"
                )
            ]
        )

        # Save updated model to GCS
        tf.saved_model.save(
            prediction_model,
            ARTIFACT_URI,
            signatures={"serving_default": serving_function},
        )

    elif args.deploy:
        print("Deploy model")

        # List of prebuilt containers for prediction
        # https://cloud.google.com/vertex-ai/docs/predictions/pre-built-containers
        serving_container_image_uri = (SERVING_CONTAINER_IMAGE_URI)

        # Upload and Deploy model to Vertex AI
        # Reference: https://cloud.google.com/python/docs/reference/aiplatform/latest/google.cloud.aiplatform.Model#google_cloud_aiplatform_Model_upload
        deployed_model = aiplatform.Model.upload(
            display_name=BEST_MODEL,
            artifact_uri=ARTIFACT_URI,
            serving_container_image_uri=serving_container_image_uri,
        )
        print("deployed_model:", deployed_model)
        # Reference: https://cloud.google.com/python/docs/reference/aiplatform/latest/google.cloud.aiplatform.Model#google_cloud_aiplatform_Model_deploy
        endpoint = deployed_model.deploy(
            deployed_model_display_name=BEST_MODEL,
            traffic_split={"0": 100},
            machine_type="n1-standard-4",
            accelerator_count=0,
            min_replica_count=1,
            max_replica_count=1,
            sync=False,
        )
        print("endpoint:", endpoint)

    elif args.predict:
        print("Predict using endpoint")

        # Get the endpoint
        # Endpoint format: endpoint_name="projects/{PROJECT_NUMBER}/locations/us-central1/endpoints/{ENDPOINT_ID}"
        print(f'MODEL_ENDPOINT : {MODEL_ENDPOINT}')
        endpoint = aiplatform.Endpoint(MODEL_ENDPOINT)

        # Get a sample image to predict
        image_files = glob(os.path.join("test_images", "*.png"))
        print("image_files:", image_files[:5])

        image_samples = np.random.randint(0, high=len(image_files) - 1, size=5)
        for img_idx in image_samples:
            print("Image:", image_files[img_idx])

            with open(image_files[img_idx], "rb") as f:
                data = f.read()
            b64str = base64.b64encode(data).decode("utf-8")
            # The format of each instance should conform to the deployed model's prediction input schema.
            instances = [{"bytes_inputs": {"b64": b64str}}]

            result = endpoint.predict(instances=instances)

            print("Result:", result)
            prediction = result.predictions[0]
            print(prediction)



if __name__ == "__main__":
    # Generate the inputs arguments parser
    # if you type into the terminal 'python cli.py --help', it will provide the description
    parser = argparse.ArgumentParser(description="Data Collector CLI")

    parser.add_argument(
        "-u",
        "--upload",
        action="store_true",
        help="Upload saved model to GCS Bucket",
    )
    parser.add_argument(
        "-d",
        "--deploy",
        action="store_true",
        help="Deploy saved model to Vertex AI",
    )
    parser.add_argument(
        "-p",
        "--predict",
        action="store_true",
        help="Make prediction using the endpoint from Vertex AI",
    )
    parser.add_argument(
        "-t",
        "--test",
        action="store_true",
        help="Test deployment to Vertex AI",
    )

    args = parser.parse_args()

    main(args)
