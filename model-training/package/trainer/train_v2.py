import os
import time
import math
import argparse
import yaml
from google.cloud import storage

# Tensorflow
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, Dense, Dropout 
from tensorflow.keras.layers import Flatten, MaxPooling2D
from tensorflow.keras.optimizers import Adam
print(f'Tensorflow Version: {tf.__version__}')
print("Eager Execution Enabled:", tf.executing_eagerly())

# Get the number of replicas
strategy = tf.distribute.MirroredStrategy()
print("Number of Replicas:", strategy.num_replicas_in_sync)

devices = tf.config.experimental.get_visible_devices()
print("Devices:", devices)
print(tf.config.experimental.list_logical_devices('GPU'))

print("GPU Available: ", tf.config.list_physical_devices('GPU'))
print("All Physical Devices", tf.config.list_physical_devices())

'''
Need to:
|--Export christina's ipynb file to py file
|  |--Include Weights and Biases callbacks
|  |--Save model to GCP bucket folder
|--Get a standardized yml file for models
|--Create pipfile, pipfile.lock and dockerfile
|--Figure out how to run with Vertex AI

'''


# Define globals
GCS_BUCKET_NAME = os.environ["GCS_BUCKET_NAME"]
tfrecords_folder = "data/tf_records/180_by_180/"
models_folder = "models/"


def build_model(
    input_shape,
    n_classes, 
    n_filters=16,
    dense_nodes=1024, 
    conv_dropout=0.25, 
    dense_dropout=0.5,  
    filter_size=(3,3), 
    pool_size=(2,2), 
    output_activation='softmax',
    model_name='model' 
    ):

    """
    This function builds a simplified vgg-like convolutional model
   
    """
    model = Sequential(
        [
            Conv2D(
                n_filters, filter_size, padding="same", activation="relu",
                input_shape=input_shape,
            ),
            Conv2D(n_filters, filter_size, padding="same", activation="relu"),
            MaxPooling2D(pool_size=pool_size),
            Dropout(conv_dropout),
            
            Conv2D(n_filters*2, filter_size, padding="same", activation="relu"),
            Conv2D(n_filters*2, filter_size, padding="same", activation="relu"),
            MaxPooling2D(pool_size=pool_size),
            Dropout(conv_dropout),

            Conv2D(n_filters*4, filter_size, padding="same", activation="relu"),
            Conv2D(n_filters*4, filter_size, padding="same", activation="relu"),
            MaxPooling2D(pool_size=pool_size),
            Dropout(conv_dropout),

            Conv2D(n_filters*8, filter_size, padding="same", activation="relu"),
            Conv2D(n_filters*8, filter_size, padding="same", activation="relu"),
            MaxPooling2D(pool_size=pool_size),
            Dropout(conv_dropout),

            Conv2D(n_filters*8, filter_size, padding="same", activation="relu"),
            Conv2D(n_filters*8, filter_size, padding="same", activation="relu"),
            MaxPooling2D(pool_size=pool_size),
            Dropout(conv_dropout),

            Flatten(),
            Dense(dense_nodes, activation="relu"),
            Dropout(dense_dropout),
            Dense(n_classes, activation=output_activation),            
        ],
        name=model_name
    )
    
    return model



# Parse a single image and label
def parse_tfrecord_example(example):
    # Read TF Records
    feature_description = {
        'image': tf.io.FixedLenFeature([], tf.string),
        'label': tf.io.FixedLenFeature([5], tf.float32, default_value=[0.0, 0.0, 0.0, 0.0, 0.0])
    }
    
    parsed_example = tf.io.parse_single_example(example, feature_description)

    # Access global variables
    global image_size, image_shape, num_classes

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


def upload_model(model, model_name):
    print(f'Uploading model to {GCS_BUCKET_NAME}')

    # Create upload folder
    upload_source = 'uploads'
    os.makedirs(upload_source, exist_ok=True)

    # Save model
    if model_name == None:
        file_name = f'model_{time.time_ns()}.h5'
    else:
        file_name = f'{model_name}_{time.time_ns()}.h5'
    model.save(os.path.join(upload_source, file_name))

    # Instantiate GCS client
    storage_client = storage.Client()
    bucket = storage_client.bucket(GCS_BUCKET_NAME)

    # Upload model
    blob = bucket.blob(os.path.join(models_folder, file_name))
    generation_match_precondition = 0
    blob.upload_from_filename(
        os.path.join(upload_source, file_name), 
        if_generation_match=generation_match_precondition
    )
    print('Upload complete')    


def download_tfrecords():
    print(f'Downloading tfrecords files from {GCS_BUCKET_NAME}')

    # Create download folder
    download_destination = 'downloads'
    os.makedirs(download_destination, exist_ok=True)

    # Instantiate GCS client
    client = storage.Client()

    # Download tfrecords locally
    blobs = client.list_blobs(GCS_BUCKET_NAME, prefix=tfrecords_folder)
    for blob in blobs:
        print(f'Downloading: {blob.name}')
        blob.download_to_filename(os.path.join(download_destination, blob.name))
    print('Download complete')


def main(args=None):

    # Read config file
    with open(args.config, 'r') as file:
        config = yaml.full_load(file)

    # Build model
    model = build_model(**config['build_params'])
    print(model.summary())

    # Set optimizer
    if config['compile_params']['optimizer'] == 'adam':
        optimizer = Adam(
            learning_rate = config['compile_params']['learning_rate']
        )

    # Compile model
    model.compile(
        loss = config['compile_params']['loss'],
        optimizer = optimizer,
        metrics = config['compile_params']['metrics']
    )

    # Define global variables for tfrecords parser
    global image_size, image_shape, num_classes
    image_size = [math.prod(config['build_params']['input_shape'])]
    image_shape = list(config['build_params']['input_shape'])
    num_classes = config['build_params']['n_classes']

    # Fetch data
    download_tfrecords()
    train_data, validation_data = load_tfrecords(
        'downloads',
        config['train_params']['batch_size']
    )

    # Train model
    start_time = time.time()
    training_results = model.fit(
            train_data,
            validation_data = validation_data,
            epochs = config['train_params']['epochs'],
            verbose = 1
    )
    execution_time = (time.time() - start_time)/60.0
    print(f'Training execution time (mins): {execution_time:.02f}')

    # Upload model
    upload_model(model, config['build_params']['model_name'])



if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description='Build a VGG-like CNN model from a YAML configuration file.'
    )

    parser.add_argument(
        '-c',
        '--config', 
        required=True,
        type=str, 
        help='Path to the YAML configuration file'
    )

    args = parser.parse_args()

    main(args)

