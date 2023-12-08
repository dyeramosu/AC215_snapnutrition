import os
import time
import math
import uuid
import argparse
import yaml
from importlib.resources import files
from trainer.utils import download_tfrecords, upload_model_weights, build_model

# Tensorflow
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # silence tf info, error, warning messages
import tensorflow as tf
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping

print(f'Tensorflow Version: {tf.__version__}')
print("Eager Execution Enabled:", tf.executing_eagerly())
strategy = tf.distribute.MirroredStrategy()
print("Number of Replicas:", strategy.num_replicas_in_sync)
devices = tf.config.experimental.get_visible_devices()
print("Devices:", devices)
print(tf.config.experimental.list_logical_devices('GPU'))
print("GPU Available: ", tf.config.list_physical_devices('GPU'))
print("All Physical Devices", tf.config.list_physical_devices())


# Weights & Biases
import wandb
from wandb.keras import WandbCallback


# Parse command line arguments
parser = argparse.ArgumentParser(
    description='Build and train a model from a YAML configuration file.'
)
parser.add_argument(
    '-w',
    '--wandb_key',
    required=True,
    type=str,
    help="Weights and Biases API Key"
)
parser.add_argument(
    '-b',
    '--bucket',
    required=True,
    type=str,
    help="GCS bucket name"
)
parser.add_argument(
    '-p',
    '--project',
    required=True,
    type=str,
    help="GCP project name"
)
parser.add_argument(
    '-tf',
    '--tfrecords_folder',
    required=True,
    type=str,
    help="TF records folder path in GCS bucket"
)
parser.add_argument(
    '-mo',
    '--models_folder',
    required=True,
    type=str,
    help="Trained models folder path in GCS bucket"
)
args = parser.parse_args()


# Login to Weights and Biases
wandb.login(key=args.wandb_key)


# Parse a single image and label
def parse_tfrecord_example(example):
    # Read TF Records
    feature_description = {
        'image': tf.io.FixedLenFeature([], tf.string),
        'label': tf.io.FixedLenFeature([5], tf.float32, default_value=[0.0, 0.0, 0.0, 0.0, 0.0])
    }

    parsed_example = tf.io.parse_single_example(example, feature_description)

    # Access global variables
    global image_size, image_shape

    # Image
    image = tf.io.decode_raw(parsed_example['image'], tf.float32)
    image.set_shape(image_size)
    image = tf.reshape(image, image_shape)

    # Label
    label = parsed_example['label']

    return image, label


# Normalize pixels
def normalize(image, label):
    image = image / 255
    return image, label


# Load train and validation data from tfrecords files
def load_tfrecords(
        tfrecords_directory,
        batch_size,
        normalize_data=False
    ):
    # Read the tfrecord files
    train_tfrecord_files = tf.data.Dataset.list_files(tfrecords_directory + '/train*')
    validate_tfrecord_files = tf.data.Dataset.list_files(tfrecords_directory + '/val*')

    # Train data
    train_data = train_tfrecord_files.flat_map(tf.data.TFRecordDataset)
    train_data = train_data.map(parse_tfrecord_example, num_parallel_calls=tf.data.AUTOTUNE)
    if normalize_data:
        train_data = train_data.map(normalize, num_parallel_calls=tf.data.AUTOTUNE)
    train_data = train_data.batch(batch_size)
    train_data = train_data.prefetch(buffer_size=tf.data.AUTOTUNE)

    # Validation data
    validation_data = validate_tfrecord_files.flat_map(tf.data.TFRecordDataset)
    validation_data = validation_data.map(parse_tfrecord_example, num_parallel_calls=tf.data.AUTOTUNE)
    if normalize_data:
        validation_data = validation_data.map(normalize, num_parallel_calls=tf.data.AUTOTUNE)
    validation_data = validation_data.batch(batch_size)
    validation_data = validation_data.prefetch(buffer_size=tf.data.AUTOTUNE)

    print("train_data", train_data)
    print("validation_data", validation_data)

    return train_data, validation_data


# Read config file
config_path = files('trainer').joinpath('model_config.yml')
with config_path.open('r') as file:
    config = yaml.full_load(file)


# Build model
model_type = config['build_params']['model_type']
config['build_params']['model_name'] = f'{model_type}-{uuid.uuid4()}'
model = build_model(**config['build_params'])
print(model.summary())


def train_model():
    # Initialize a Weights & Biases run
    wandb.init(
        project="snapnutrition-training-vertex-ai"
    )

    # Set optimizer
    if config['compile_params']['optimizer'] == 'adam':
        optimizer = Adam(
            learning_rate=wandb.config.learning_rate
        )
    else:
        optimizer = Adam()

    # Set metrics
    for i, metric in enumerate(config['compile_params']['metrics']):
        if metric == 'rmse':
            config['compile_params']['metrics'][i] = tf.keras.metrics.RootMeanSquaredError()

    # Compile model
    model.compile(
        loss=wandb.config.loss,
        optimizer=optimizer,
        metrics=config['compile_params']['metrics']
    )

    # Define global variables for tfrecords parser
    global image_size, image_shape
    image_size = [math.prod(config['build_params']['input_shape'])]
    image_shape = list(config['build_params']['input_shape'])

    # Fetch data
    download_tfrecords(args.bucket, args.project, args.tfrecords_folder)
    train_data, validation_data = load_tfrecords(
        'downloads',
        wandb.config.batch_size,
        normalize_data=False
    )

    # Early Stopping
    if config['train_params']['early_stopping'] == True:
        early_stopping = EarlyStopping(
            monitor='val_loss',
            patience=config['train_params']['patience'],
            restore_best_weights=True,
            start_from_epoch=int(config['train_params']['epochs'] * 0.25)
        )
        callbacks = [WandbCallback(save_weights_only=True), early_stopping]
    else:
        callbacks = [WandbCallback(save_weights_only=True)]

    # Train model
    start_time = time.time()
    model.fit(
        train_data,
        validation_data=validation_data,
        epochs=wandb.config.epochs,
        callbacks=callbacks,
        verbose='auto'
    )
    execution_time = (time.time() - start_time) / 60.0
    print(f'Training execution time (mins): {execution_time:.02f}')


# Define sweep parameters
sweep_configs = {
    "name": model_type,
    "method": "grid",
    "metric": {"name": "mse", "goal": "minimize"},
    "parameters": {
        "learning_rate": {"values": [0.001]},
        "epochs": {"values": [100]},
        "loss": {"values": ["mae", "mse"]},
        "batch_size": {"values": [4, 8, 16, 32, 64, 128]},
    }
}


# Initiate sweeps
sweep_id = wandb.sweep(
    sweep_configs, 
    project='snapnutrition-training-vertex-ai'
)
wandb.agent(
    sweep_id=sweep_id, 
    function=train_model
)


# Close the W&B run
wandb.finish()


print("Training Job Complete")
