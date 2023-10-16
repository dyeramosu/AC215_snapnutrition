import os
import time
import math
import uuid
import argparse
import yaml
from importlib.resources import files
from trainer.utils import download_tfrecords, upload_model_weights
from trainer.models import DefaultModel


# Tensorflow
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' # silence tf info, error, warning messages
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, Dense, Dropout 
from tensorflow.keras.layers import Flatten, MaxPooling2D
from tensorflow.keras.optimizers import Adam
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
    description='Build a VGG-like CNN model from a YAML configuration file.'
)

parser.add_argument(
    '-w',
    '--wandb_key',
    required=True,
    type=str, 
    help="Weights and Biases API Key"
)

args = parser.parse_args()


# Define globals
GCS_BUCKET_NAME = "snapnutrition_data_bucket" #os.path.basename(os.environ["GCS_BUCKET_URI"])
GCP_PROJECT = "csci-115-398800" # os.environ["GCP_PROJECT"]
tfrecords_folder = "data/tf_records/180_by_180/"
models_folder = "models/"


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
    image = tf.io.decode_raw(parsed_example['image'], tf.uint8)
    image.set_shape(image_size)
    image = tf.reshape(image, image_shape)
    
    # Label
    label = parsed_example['label']

    return image, label


# Normalize pixels
def normalize(image, label):
    image = image/255
    return image, label


# Load train and validation data from tfrecords files
def load_tfrecords(
        tfrecords_directory,
        batch_size
    ):

    # Read the tfrecord files
    train_tfrecord_files = tf.data.Dataset.list_files(tfrecords_directory+'/train*')
    validate_tfrecord_files = tf.data.Dataset.list_files(tfrecords_directory+'/val*')

    # Train data
    train_data = train_tfrecord_files.flat_map(tf.data.TFRecordDataset)
    train_data = train_data.map(parse_tfrecord_example, num_parallel_calls=tf.data.AUTOTUNE)
    train_data = train_data.map(normalize, num_parallel_calls=tf.data.AUTOTUNE)
    train_data = train_data.batch(batch_size)
    train_data = train_data.prefetch(buffer_size=tf.data.AUTOTUNE)

    # Validation data
    validation_data = validate_tfrecord_files.flat_map(tf.data.TFRecordDataset)
    validation_data = validation_data.map(parse_tfrecord_example, num_parallel_calls=tf.data.AUTOTUNE)
    validation_data = validation_data.map(normalize, num_parallel_calls=tf.data.AUTOTUNE)
    validation_data = validation_data.batch(batch_size)
    validation_data = validation_data.prefetch(buffer_size=tf.data.AUTOTUNE)

    print("train_data",train_data)
    print("validation_data",validation_data)

    return train_data, validation_data


# Read config file
config_path = files('trainer').joinpath('model_config.yml')
with config_path.open('r') as file:
    config = yaml.full_load(file)


# Build model
if config['build_params']['model_name'] == 'test':
    model_name = config['build_params']['model_name']
    config['build_params']['model_name'] = f'{model_name}_{uuid.uuid4()}'
    model = DefaultModel(**config['build_params'])
else:
    model_name = 'default'
    config['build_params']['model_name'] = f'{model_name}_{uuid.uuid4()}'
    model = DefaultModel(**config['build_params'])
model.build((None,) + config['build_params']['input_shape'])    
print(model.summary())


# Set optimizer
if config['compile_params']['optimizer'] == 'adam':
    optimizer = Adam(
        learning_rate = config['compile_params']['learning_rate']
    )
else:
    optimizer = Adam()


# Set metrics
for i, metric in enumerate(config['compile_params']['metrics']):
    if metric ==  'rmse':
        config['compile_params']['metrics'][i] = tf.keras.metrics.RootMeanSquaredError()


# Compile model
model.compile(
    loss = config['compile_params']['loss'],
    optimizer = optimizer,
    metrics = config['compile_params']['metrics']
)


# Define global variables for tfrecords parser
global image_size, image_shape
image_size = [math.prod(config['build_params']['input_shape'])]
image_shape = list(config['build_params']['input_shape'])


# Fetch data
download_tfrecords(GCS_BUCKET_NAME, GCP_PROJECT, tfrecords_folder)
train_data, validation_data = load_tfrecords(
    'downloads',
    config['train_params']['batch_size']
)


# Initialize a Weights & Biases run
wandb.init(
    project="snapnutrition-training-vertex-ai",
    config=config,
    name=model.name,
)

# Train model
start_time = time.time()
training_results = model.fit(
        train_data,
        validation_data = validation_data,
        epochs = config['train_params']['epochs'],
        callbacks=[WandbCallback()],
        verbose = 1
)
execution_time = (time.time() - start_time)/60.0
print(f'Training execution time (mins): {execution_time:.02f}')


# Upload model weights
upload_model_weights(model, GCS_BUCKET_NAME, GCP_PROJECT, models_folder)


# Update W&B
wandb.config.update({"execution_time": execution_time})


# Close the W&B run
wandb.run.finish()


print("Training Job Complete")
