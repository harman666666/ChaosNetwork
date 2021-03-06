import tensorflow as tf
import numpy as np


def fc_layer(input_, input_size, output_size, activation=None, bias=True, scope=None, dtype=tf.float32):
    '''
        fully connnected layer
        Args :
            input_  - 2D tensor
                general shape : [batch, input_size]
            output_size - int
                shape of output 2D tensor
            activation - activation function
                defaults to be None
            scope - string
                defaults to be None then scope becomes "fc"
    '''
    with tf.variable_scope(scope or "fc") as sc:
        try:
            w = tf.get_variable(name="weight", shape=[input_size, output_size],
                            initializer=tf.contrib.layers.xavier_initializer(seed=2), dtype=dtype)

        except ValueError:
            sc.reuse_variables()
            w = tf.get_variable(name="weight", shape=[input_size, output_size],  
                                initializer=tf.contrib.layers.xavier_initializer(seed=2), dtype=dtype)
        output_ = tf.matmul(input_, w)
        if bias:
            b = tf.get_variable(name="bias", shape=[output_size], initializer=tf.constant_initializer(0.001), dtype=dtype)
            output_ += b
        return output_ if activation is None else activation(output_)

