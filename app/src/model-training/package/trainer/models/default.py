import tensorflow as tf


def default_model(
    input_shape,
    n_classes, 
    n_filters=16,
    dense_nodes=1024, 
    conv_dropout=0.25, 
    dense_dropout=0.5,  
    filter_size=(3,3), 
    pool_size=(2,2), 
    filter_multipliers=[1,2,4,8,8],
    output_activation='linear',
    model_name='default',
    **kwargs 
    ):

    """
    This function returns a simplified vgg-like convolutional model
    
    Arguments:
        input_shape: shape of the training data (row, column, channel)
        n_classes: number of output classes
        n_filters: number of filters passed to a convolutional layer
        dense_nodes: number of nodes for the dense layer
        conv_dropout: dropout rate for convolutional blocks
        dense_dropout: dropout rate for dense layer
        filter_size: size of each filter (row, column)
        pool_size: size of pool filter (row, column)
        filter multipliers: list of integers that set conv filter growth scheme
        output_activatiion: allows reuse for classification models
        model_name: unique name for model

    """

    layers = []

    # Define convolutional blocks
    for i, multiplier in enumerate(filter_multipliers):
        
        if i == 0:
            conv1 = tf.keras.layers.Conv2D(
                n_filters*multiplier, 
                filter_size, 
                padding="same", 
                activation="relu",
                input_shape=input_shape
            )
        else:
            conv1 = tf.keras.layers.Conv2D(
                n_filters*multiplier, 
                filter_size, 
                padding="same", 
                activation="relu",
            )
        conv2 = tf.keras.layers.Conv2D(
            n_filters*multiplier, 
            filter_size, 
            padding="same", 
            activation="relu",
        )
        pool = tf.keras.layers.MaxPooling2D(pool_size=pool_size)
        dropout = tf.keras.layers.Dropout(conv_dropout)
        layers.extend([conv1, conv2, pool, dropout])

    # Define dense layers
    layers.extend([
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(dense_nodes, activation='relu'),
        tf.keras.layers.Dropout(dense_dropout),
        tf.keras.layers.Dense(n_classes, activation=output_activation)
    ])
    
    return tf.keras.models.Sequential(layers, name=model_name)
