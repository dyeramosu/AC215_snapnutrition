import tensorflow as tf

def efficientnet_b7_model(
    input_shape,
    n_classes, 
    dense_nodes=1024, 
    kernel_weight = 0.02,
    bias_weight = 0.02,
    output_activation='linear',
    model_name='efficientnet_b7',
    train_base=False,
    **kwargs 
):

    """
    This function returns a efficientnet_b7 transfer learning model
    
    Arguments:
        input_shape: shape of the training data (row, column, channel)
        n_classes: number of output classes
        dense_nodes: number of nodes for the dense layer
        conv_dropout: dropout rate after the global pooling layer 
        dense_dropout: dropout rate after the dense layer
        output_activation: allows reuse for classification models
        model_name: unique name for model
        train_base: train the transfer model layers or not (True/False)
    
    Note:
        For EfficientNet, input preprocessing is included as part of the 
        model (as a Rescaling layer), and thus 
        tf.keras.applications.efficientnet.preprocess_input is actually 
        a pass-through function. EfficientNet models expect their inputs 
        to be float tensors of pixels with values in the [0-255] range.
    
    """

    # Load a pretrained model from keras.applications
    tranfer_model_base = tf.keras.applications.efficientnet.EfficientNetB7(
        input_shape=input_shape, 
        weights="imagenet", 
        include_top=False
    )

    # Freeze the mobileNet model layers
    tranfer_model_base.trainable = train_base

    # Build model
    inputs = tf.keras.Input(shape=input_shape)
    x = tf.keras.applications.efficientnet.preprocess_input(inputs)
    x = tranfer_model_base(x, training=False)
    x = tf.keras.layers.GlobalAveragePooling2D()(x)
    x = tf.keras.layers.Dense(
            units=dense_nodes,
            activation="relu",
            kernel_regularizer=tf.keras.regularizers.l1(kernel_weight),
            bias_regularizer=tf.keras.regularizers.l1(bias_weight),
        )(x)
    outputs = tf.keras.layers.Dense(
            units=n_classes,
            activation=output_activation,
            kernel_regularizer=tf.keras.regularizers.l1(kernel_weight),
            bias_regularizer=tf.keras.regularizers.l1(bias_weight),
        )(x)
    
    return tf.keras.Model(inputs, outputs, name=model_name)