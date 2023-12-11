import tensorflow as tf

def resnet50_model(
    input_shape,
    n_classes, 
    dense_nodes=1024, 
    kernel_weight = 0.02,
    bias_weight = 0.02,
    output_activation='linear',
    model_name='resnet50',
    train_base=False,
    **kwargs 
):

    """
    This function returns a resnet50 transfer learning model
    
    Arguments:
        input_shape: shape of the training data (row, column, channel)
        n_classes: number of output classes
        dense_nodes: number of nodes for the dense layer
        kernel_weight: L1 regularizer weight for dense layer kernel
        bias_weight: L1 regularizer weight for dense layer bias
        output_activation: allows reuse for classification models
        model_name: unique name for model
        train_base: train the transfer model layers or not (True/False)
    
    Note: 
        For ResNet, call tf.keras.applications.resnet.preprocess_input on 
        your inputs before passing them to the model. resnet.preprocess_input 
        will convert the input images from RGB to BGR, then will zero-center 
        each color channel with respect to the ImageNet dataset, without scaling.
    """

    # Load a pretrained model from keras.applications
    tranfer_model_base = tf.keras.applications.resnet50.ResNet50(
        input_shape=input_shape, 
        weights="imagenet", 
        include_top=False
    )

    # Freeze the resnet50 model layers
    tranfer_model_base.trainable = train_base

    # Build model
    inputs = tf.keras.Input(shape=input_shape)
    x = tf.keras.applications.resnet50.preprocess_input(inputs) # Preprocess for ResNet50
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