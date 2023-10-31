import os
import time
import math
import uuid
import argparse
import yaml
from importlib.resources import files
from trainer.utils import download_tfrecords, upload_model_weights, build_model


# Tensorflow
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' # silence tf info, error, warning messages
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
    image = image/255
    return image, label


# Load train and validation data from tfrecords files
def load_tfrecords(
        tfrecords_directory,
        batch_size,
        normalize_data=False
    ):
    # Read the tfrecord files
    train_tfrecord_files = tf.data.Dataset.list_files(tfrecords_directory+'/train*')
    validate_tfrecord_files = tf.data.Dataset.list_files(tfrecords_directory+'/val*')

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

    print("train_data",train_data)
    print("validation_data",validation_data)

    return train_data, validation_data


# Read config file
config_path = files('trainer').joinpath('model_config.yml')
with config_path.open('r') as file:
    config = yaml.full_load(file)


# Create hyperparameter dictionary for Weights & Biases
wandb_config = {
    'input_shape': config['build_params']['input_shape'],
    'loss': config['compile_params']['loss'],
    'optimizer': config['compile_params']['optimizer'],
    'learning_rate': config['compile_params']['learning_rate'],
    'metrics': config['compile_params']['metrics'],
    'batch_size': config['train_params']['batch_size'],
    'epochs': config['train_params']['epochs']
}


# Build model
model_type = config['build_params']['model_type']
config['build_params']['model_name'] = f'{model_type}-{uuid.uuid4()}'
model = build_model(**config['build_params'])
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
download_tfrecords(args.bucket, args.project, args.tfrecords_folder)
train_data, validation_data = load_tfrecords(
    'downloads',
    config['train_params']['batch_size'],
    normalize_data=False
)


# Initialize a Weights & Biases run
run = wandb.init(
    project="snapnutrition-training-vertex-ai",
    config=wandb_config,
    name=model.name,
)


# Log the model build code to the W&B run
model_build_path = files('trainer').joinpath('models')
run.log_code(
    root=model_build_path,
    name=model_type,
    include_fn=lambda path: path.endswith(f'{model_type}.py'),
)


# Early Stopping 
if config['train_params']['early_stopping'] == True:
    early_stopping = EarlyStopping(
        monitor='val_loss', 
        patience=config['train_params']['patience'], 
        restore_best_weights=True, 
        start_from_epoch=20
    )
    callbacks = [WandbCallback(save_weights_only=True), early_stopping]
else:
    callbacks = [WandbCallback(save_weights_only=True)]


# Train model
start_time = time.time()
training_results = model.fit(
        train_data,
        validation_data = validation_data,
        epochs = config['train_params']['epochs'],
        callbacks=callbacks,
        verbose = 'auto'
)
execution_time = f'{(time.time()-start_time)/60.0:.02f} mins'
print(f'Training execution time:', execution_time)


# Upload model weights
upload_model_weights(model, args.bucket, args.project, args.models_folder)


# Update W&B
run.config.update({"execution_time": execution_time})


# Close the W&B run
run.finish()


# Fine tune model
if config['train_params']['fine_tune'] == True:

    # Fetch data again
    train_data, validation_data = load_tfrecords(
        'downloads',
        config['train_params']['batch_size'],
        normalize_data=False
    )

    # Reset optimizer for 100x smaller learning rate
    learning_rate = config['compile_params']['learning_rate'] / 100.
    wandb_config['learning_rate'] = learning_rate

    # Initialize a Weights & Biases run
    run2 = wandb.init(
        project="snapnutrition-training-vertex-ai",
        config=wandb_config,
        name='fine_tuned-'+model.name,
    )

    # Log the model build code to the W&B run
    model_build_path = files('trainer').joinpath('models')
    run2.log_code(
        root=model_build_path,
        name=model_type,
        include_fn=lambda path: path.endswith(f'{model_type}.py'),
    )

    # Clone the model and set all trainable parameters to True
    config['build_params']['model_name'] = f'fine_tuned-{model.name}'
    fine_tuned = build_model(**config['build_params'])
    weights_path =  f'uploads/{model.name}.h5'
    fine_tuned.load_weights(weights_path)
    fine_tuned.trainable = True # set weights to trainable for fine tuning

    # Set optimizer
    if config['compile_params']['optimizer'] == 'adam':
        optimizer = Adam(learning_rate=learning_rate)
    else:
        optimizer = Adam()

    # Set metrics
    for i, metric in enumerate(config['compile_params']['metrics']):
        if metric ==  'rmse':
            config['compile_params']['metrics'][i] = tf.keras.metrics.RootMeanSquaredError()

    # Recompile model
    fine_tuned.compile(
        loss = config['compile_params']['loss'],
        optimizer = optimizer,
        metrics = config['compile_params']['metrics']
    )

    # Retrain
    start_time = time.time()
    training_results = fine_tuned.fit(
            train_data,
            validation_data = validation_data,
            epochs = config['train_params']['epochs'],
            callbacks=callbacks,
            verbose = 'auto'
    )
    execution_time = f'{(time.time()-start_time)/60.0:.02f} mins'
    print(f'Training execution time:', execution_time)


    # Upload model weights
    upload_model_weights(fine_tuned, args.bucket, args.project, args.models_folder)

    # Update W&B
    run2.config.update({"execution_time": execution_time})

    # Close the W&B run
    run2.finish()


print("Training Job Complete")