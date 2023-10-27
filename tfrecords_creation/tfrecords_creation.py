import pandas as pd
import os
import time
import tensorflow as tf
import shutil

import numpy as np
# Dask
import dask
import dask.dataframe as dd
import dask.delayed as delayed
from dask.diagnostics import ProgressBar
import cv2

print("Begin processing....")

# paths to read train test val data (has image filepaths and corresponding labels
TRAIN_SAVE_PATH = "./snapnutrition_data_bucket/data/processed_labels/train_data.pickle"
VAL_SAVE_PATH = "./snapnutrition_data_bucket/data/processed_labels/validation_data.pickle"
TEST_SAVE_PATH = "./snapnutrition_data_bucket/data/processed_labels/test_data.pickle"

# Variables for Resizing Images
IMAGE_HEIGHT = 180
IMAGE_WIDTH = 180
NUM_CHANNELS = 3

# Split data into multiple TFRecord shards between 100MB to 200MB
NUM_TRAIN_SHARDS = 12
NUM_TEST_VAL_SHARDS = 4

# output directory for this tfrecord creation script
TFRECORD_SAVE_PATH = './snapnutrition_data_bucket/data/tf_records/180_by_180_dask_normalized'
# Create an output path to store the tfrecords
if os.path.exists(TFRECORD_SAVE_PATH):
    shutil.rmtree(TFRECORD_SAVE_PATH)
tf.io.gfile.makedirs(TFRECORD_SAVE_PATH)

# read train, test, validation data from pickle files
train_xy = pd.read_pickle(TRAIN_SAVE_PATH)
validate_xy = pd.read_pickle(VAL_SAVE_PATH)
test_xy = pd.read_pickle(TEST_SAVE_PATH)


@dask.delayed
def read_resize_image(file_path):
  # read image
  image = cv2.imread(file_path)
  # convert to rgb
  image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
  # Resize image
  image = cv2.resize(image, (IMAGE_WIDTH,IMAGE_HEIGHT), interpolation = cv2.INTER_AREA)

  return image

def create_tf_example(item, dask_metrics):
    # Read image
    image = tf.io.read_file(item[1])
    image = tf.image.decode_png(image, channels=NUM_CHANNELS)
    image = tf.image.resize(image, [IMAGE_HEIGHT, IMAGE_WIDTH])

    # Custom Normalize image with pre-calculated Dask Metrics
    image = (tf.cast(image, tf.float32) - dask_metrics['mean']) / dask_metrics['stdev']
    # # Encode
    # image = tf.cast(image, tf.uint8)
    # image = tf.image.encode_jpeg(image, optimize_size=True, chroma_downsampling=False)
    # image = tf.cast(image, tf.uint8)

    # Label
    label = item[0]

    # Build feature dict
    feature_dict = {
        'image': tf.train.Feature(bytes_list=tf.train.BytesList(value=[image.numpy().tobytes()])),
        'label': tf.train.Feature(float_list=tf.train.FloatList(value=label)),
    }

    example = tf.train.Example(features=tf.train.Features(feature=feature_dict))
    return example


def create_tf_records(data, dask_metrics, num_shards=10, prefix='', folder='data'):
    #first use dask to calculate mean


    num_records = len(data)
    step_size = num_records // num_shards + 1

    for i in range(0, num_records, step_size):
        print("Creating shard:", (i // step_size), " from records:", i, "to", (i + step_size))
        path = '{}/{}_000{}.tfrecords'.format(folder, prefix, i // step_size)
        print(path)

        # Write the file
        with tf.io.TFRecordWriter(path) as writer:
            # Filter the subset of data to write to tfrecord file
            for item in data[i:i + step_size]:
                tf_example = create_tf_example(item, dask_metrics)
                writer.write(tf_example.SerializeToString())

#Let's get image mean and stdev from train dataset
full_train_val = train_xy + validate_xy
lazy_loaded_images = [read_resize_image(path_and_label[1]) for path_and_label in full_train_val]
image_arrays = [dask.array.from_delayed(img,dtype=np.uint8,shape=(IMAGE_WIDTH, IMAGE_HEIGHT, NUM_CHANNELS)) for img in lazy_loaded_images]
all_images_dask = dask.array.stack(image_arrays, axis=0)

start_time = time.time()
dask_computed_metrics = {}
mean, stdev = dask.compute(all_images_dask.mean(axis=(0,1, 2)), all_images_dask.std(axis=(0,1, 2)))
print("mean:", mean)
print("stdev:", stdev)
dask_computed_metrics ["mean"] = mean
dask_computed_metrics ["stdev"] = stdev
execution_time = (time.time() - start_time)/60.0
print("Execution time (mins)",execution_time)

# Create TF Records for train
start_time = time.time()
create_tf_records(train_xy, dask_computed_metrics, num_shards=NUM_TRAIN_SHARDS, prefix="train", folder=TFRECORD_SAVE_PATH)
execution_time = (time.time() - start_time) / 60.0
print("Train TFRecords Execution time (mins)", execution_time)

# Create TF Records for validation
start_time = time.time()
create_tf_records(validate_xy, dask_computed_metrics, num_shards=NUM_TEST_VAL_SHARDS, prefix="val", folder=TFRECORD_SAVE_PATH)
execution_time = (time.time() - start_time) / 60.0
print("Validation TFRecords Execution time (mins)", execution_time)

# Create TF Records for test
start_time = time.time()
create_tf_records(test_xy, dask_computed_metrics, num_shards=NUM_TEST_VAL_SHARDS, prefix="test", folder=TFRECORD_SAVE_PATH)
execution_time = (time.time() - start_time) / 60.0
print("Test TFRecords Execution time (mins)", execution_time)
