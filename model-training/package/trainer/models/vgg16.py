import tensorflow as tf

def vgg16_model(
    input_shape,
    n_classes, 
    dense_nodes=1024, 
    kernel_weight = 0.02,
    bias_weight = 0.02,
    output_activation='linear',
    model_name='vgg16',
    train_base=False,
    **kwargs 
):

    """
    This function returns a vgg16 transfer learning model
    
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
    tranfer_model_base = tf.keras.applications.VGG16(
        input_shape=input_shape, 
        weights="imagenet", 
        include_top=False
    )

    # Freeze the mobileNet model layers
    tranfer_model_base.trainable = train_base

    # Build model
    model = tf.keras.models.Sequential(
        [
            tranfer_model_base,
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