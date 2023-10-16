import tensorflow as tf


class ConvBlock(tf.keras.layers.Layer):
    """
    Convolutional block consisting of (conv-> conv-> max_pool-> dropout)
    
    """
    def __init__(
            self, 
            n_filters,
            filter_size, 
            pool_size, 
            conv_dropout, 
        ):
        super().__init__()
        self.conv1 = tf.keras.layers.Conv2D(
            n_filters, 
            filter_size, 
            padding="same", 
            activation="relu",
        )
        self.conv2 = tf.keras.layers.Conv2D(
            n_filters, 
            filter_size, 
            padding="same", 
            activation="relu",
        )
        self.max_pool = tf.keras.layers.MaxPooling2D(pool_size=pool_size)
        self.dropout = tf.keras.layers.Dropout(conv_dropout)
    
    def call(self, x):
        x = self.conv1(x)
        x = self.conv2(x)
        x = self.max_pool(x)
        output = self.dropout(x)
        return output
  

class DefaultModel(tf.keras.Model):
    """
    This class defines a simplified vgg-like convolutional model
    
    Arguments:
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
    def __init__(
            self, 
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
        super().__init__(name=model_name)

        # Define convolutional blocks
        self.conv_blocks = []
        for multiplier in filter_multipliers:
            self.conv_blocks.append(
                ConvBlock(
                    n_filters*multiplier,
                    filter_size, 
                    pool_size, 
                    conv_dropout
                )
            )

        # Define dense layers
        self.flatten = tf.keras.layers.Flatten()
        self.dense1 = tf.keras.layers.Dense(dense_nodes, activation='relu')
        self.dense_dropout = tf.keras.layers.Dropout(dense_dropout)
        self.output_layer = tf.keras.layers.Dense(n_classes, activation=output_activation)


    def call(self, x):
        
        # Iterate through conv blocks and add to the model
        for i in range(len(self.conv_blocks)):
            x = self.conv_blocks[i](x)

        # Add the dense layers to the model
        x = self.flatten(x)
        x = self.dense1(x)
        x = self.dense_dropout(x)
        output = self.output_layer(x)
        return output
