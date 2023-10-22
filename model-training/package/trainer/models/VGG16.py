import tensorflow as tf
from tensorflow.keras.applications import VGG16
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Flatten

def VGG16_model(
    input_shape,
    n_classes, 
    dense_nodes=1024, 
    kernel_weight = 0.02,
    bias_weight = 0.02,
    output_activation='linear',
    model_name='VGG16',
    train_base=False,
    **kwargs 
):

    """
    This function returns a VGG16 transfer learning model
    
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

    # Load a pretrained model from keras.applications
    base_model = VGG16(weights='imagenet', include_top=False, input_shape=input_shape)

    # Freeze the mobileNet model layers
    base_model.trainable = train_base

    # Build model
    model = tf.keras.models.Sequential(
        [
            base_model,
            tf.keras.layers.GlobalAveragePooling2D(),
            tf.keras.layers.Dense(
                units=dense_nodes,
                activation="relu",
                kernel_regularizer=tf.keras.regularizers.l1(kernel_weight),
                bias_regularizer=tf.keras.regularizers.l1(bias_weight),
            ),
            tf.keras.layers.Dense(
                units=n_classes,
                activation=output_activation,
                kernel_regularizer=tf.keras.regularizers.l1(kernel_weight),
                bias_regularizer=tf.keras.regularizers.l1(bias_weight),
            ),
        ],
        name=model_name,
    )

    return model
