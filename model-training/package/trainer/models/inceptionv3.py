import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import Model, Sequential
import tensorflow_hub as hub

def inceptionv3_model(
    input_shape,
    n_classes, 
    dense_nodes=1024, 
    kernel_weight = 0.02,
    bias_weight = 0.02,
    output_activation='linear',
    model_name='inceptionv3',
    train_base=False,
    **kwargs 
):

    """
    This function returns a mobilenet transfer learning model
    
    Arguments:
        input_shape: shape of the training data (row, column, channel)
        n_classes: number of output classes
        dense_nodes: number of nodes for the dense layer
        kernel_weight: L1 regularizer weight for dense layer kernel
        bias_weight: L1 regularizer weight for dense layer bias
        output_activation: allows reuse for classification models
        model_name: unique name for model
        train_base: train the transfer model layers or not (True/False)
    
    """

    # ResNet50 handle to pretrained model
    handle = "https://tfhub.dev/google/imagenet/inception_v3/feature_vector/5"

    model = Sequential([
            keras.layers.InputLayer(input_shape=input_shape),
                                    hub.KerasLayer(handle, trainable=train_base),
            keras.layers.Dense(units=dense_nodes, activation=output_activation),
            keras.layers.Dense(units=n_classes)
    ], name=model_name)

    return model