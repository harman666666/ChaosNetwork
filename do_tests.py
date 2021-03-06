
import tensorflow as tf
import numpy as np
import datetime
from chaos_version_1 import ChaosNetwork

# Import MNIST data
from tensorflow.examples.tutorials.mnist import input_data
mnist = input_data.read_data_sets("/tmp/data/", one_hot=True)

# Network Parameters

n_input = 784  # MNIST data input (img shape: 28*28)
n_classes = 10  # MNIST total classes (0-9 digits)
# tf Graph Input
# mnist data image of shape 28*28=784
x = tf.placeholder(tf.float32, [None, 784], name='InputData')
# 0-9 digits recognition => 10 classes
y = tf.placeholder(tf.float32, [None, 10], name='LabelData')
# Create model
def multilayer_perceptron(x, weights, biases):
    # Hidden layer with RELU activation
    layer_1 = tf.add(tf.matmul(x, weights['w1']), biases['b1'])
    layer_1 = tf.nn.relu(layer_1)
    # Create a summary to visualize the first layer ReLU activation
    tf.summary.histogram("relu1", layer_1)
    # Hidden layer with RELU activation
    layer_2 = tf.add(tf.matmul(layer_1, weights['w2']), biases['b2'])
    layer_2 = tf.nn.relu(layer_2)
    # Create another summary to visualize the second layer ReLU activation
    tf.summary.histogram("relu2", layer_2)
    # Output layer
    out_layer = tf.add(tf.matmul(layer_2, weights['w3']), biases['b3'])
    return out_layer

def baseline():
    # Parameters
    learning_rate = 0.1
    training_epochs = 2000
    batch_size = 10
    display_step = 1
    logs_path = "./fc_net_baseline_logs/" + str(datetime.datetime.now()) + "/"
    
    n_hidden_1 = 256  # 1st layer number of features
    n_hidden_2 = 256  # 2nd layer number of features
        # Store layers weight & bias
    weights = {
        'w1': tf.Variable(tf.random_normal([n_input, n_hidden_1]), name='W1'),
        'w2': tf.Variable(tf.random_normal([n_hidden_1, n_hidden_2]), name='W2'),
        'w3': tf.Variable(tf.random_normal([n_hidden_2, n_classes]), name='W3')
    }
    biases = {
        'b1': tf.Variable(tf.random_normal([n_hidden_1]), name='b1'),
        'b2': tf.Variable(tf.random_normal([n_hidden_2]), name='b2'),
        'b3': tf.Variable(tf.random_normal([n_classes]), name='b3')
    }


    # Encapsulating all ops into scopes, making Tensorboard's Graph
    # Visualization more convenient
    with tf.name_scope('Model'):
        # Build model
        pred = multilayer_perceptron(x, weights, biases)
    with tf.name_scope('Loss'):
        # Softmax Cross entropy (cost function)
        loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=pred, labels=y))
    with tf.name_scope('SGD'):
        # Gradient Descent
        optimizer = tf.train.GradientDescentOptimizer(learning_rate)
        # Op to calculate every variable gradient
        grads = tf.gradients(loss, tf.trainable_variables())
        grads = list(zip(grads, tf.trainable_variables()))
        # Op to update all variables according to their gradient
        apply_grads = optimizer.apply_gradients(grads_and_vars=grads)
    with tf.name_scope('Accuracy'):
        # Accuracy
        acc = tf.equal(tf.argmax(pred, 1), tf.argmax(y, 1))
        acc = tf.reduce_mean(tf.cast(acc, tf.float32))
    # Initializing the variables
    init = tf.global_variables_initializer()
    # Create a summary to monitor cost tensor
    tf.summary.scalar("loss", loss)
    # Create a summary to monitor accuracy tensor
    tf.summary.scalar("accuracy", acc)
    # Create summaries to visualize weights
    for var in tf.trainable_variables():
        tf.summary.histogram(var.name, var)
    # Summarize all gradients
    for grad, var in grads:
        tf.summary.histogram(var.name + '/gradient', grad)
    # Merge all summaries into a single op
    merged_summary_op = tf.summary.merge_all()
    # Launch the graph
    with tf.Session() as sess:
        sess.run(init)
        # op to write logs to Tensorboard
        summary_writer = tf.summary.FileWriter(logs_path,
                                            graph=tf.get_default_graph())
        # Training cycle
        for epoch in range(training_epochs):
            avg_cost = 0.
            total_batch = int(mnist.train.num_examples / batch_size)
            # Loop over all batches
            for i in range(total_batch):
                batch_xs, batch_ys = mnist.train.next_batch(batch_size)
                # Run optimization op (backprop), cost op (to get loss value)
                # and summary nodes
                _, c, summary = sess.run([apply_grads, loss, merged_summary_op],
                                        feed_dict={x: batch_xs, y: batch_ys})
                # Write logs at every iteration
                summary_writer.add_summary(summary, epoch * total_batch + i)
                # Compute average loss
                avg_cost += c / total_batch
            # Display logs per epoch step
            if (epoch + 1) % display_step == 0:
                print("Epoch:", '%04d' % (epoch + 1), "cost=", "{:.9f}".format(avg_cost))
        print("Optimization Finished!")
        # Test model
        # Calculate accuracy
        print("Accuracy:", acc.eval({x: mnist.test.images, y: mnist.test.labels}))
        print("Run the command line:\n" \
            "--> tensorboard --logdir=/tmp/tensorflow_logs " \
            "\nThen open http://0.0.0.0:6006/ into your web browser")

def chaosGraphBaseline(test_name=str(datetime.datetime.now()), checkpoint_iter=0, save_output_to_file = True):
    # Parameters
    learning_rate = 0.1
    training_epochs = 2000
    batch_size = 5
    
    print("LEARNING RATE IS: " + str(learning_rate))
    print("TRAINING_EPOCHS IS: " + str(training_epochs))
    print("BATCH_size is: " + str(batch_size))

    chaos_test_path = "chaos_tests" + "/" + test_name 
    
    
    if save_output_to_file: 
        import sys
        import os    
        
        output_file = chaos_test_path + "/stdout.txt"
        
        if not os.path.exists(os.path.dirname(output_file)):
            try:
                os.makedirs(os.path.dirname(output_file))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
        
       
        sys.stdout = open(output_file, 'w+') # redirects output to this file

        save_every = 100

        logs_path = chaos_test_path + '/logs'
        checkpoint_path = chaos_test_path + "/chaos_checkpoints";

    # TODO: DECOUPLE INPUT AND OUTPUT PROJECTION LAYER INSIDE CHAOS NETWORK FROM 
    # THE CHAOS NETWORK ITSELF.
    # PPL USING API SHOULD BE BUILDING WHATEVER NETS THEY WANT AND ADD
    # CHAOS NET AS A LAYER IN THEIR ARCHITECTURE. 
    
    x = tf.placeholder(tf.float32, [None, 784], name='InputData')
    # 0-9 digits recognition => 10 classes
    y = tf.placeholder(tf.float32, [None, 10], name='LabelData')

    chaos_net = ChaosNetwork(number_of_nodes=12, # 30 nodes, 3 degree, 6 nodes in candidate field.  
                           input_size=n_input, 
                           output_size=n_classes, 
                           chaos_number=3,
                           batch_size=batch_size)
    
    train, train_loss, compute_grads = chaos_net.train(x, y)
    error, loss_op, accuracy = chaos_net.test(x, y)


    test_error_summary = tf.summary.scalar("testError", error)
    test_loss_summary = tf.summary.scalar("testLoss", loss_op)
    test_accuracy_summary = tf.summary.scalar("testAccuracy", accuracy)
    test_summary_op = tf.summary.merge([test_error_summary, test_accuracy_summary, test_loss_summary])

    train_grad_summ_op = tf.summary.merge([tf.summary.histogram("%s-grad" % g[1].name, g[0]) for g in compute_grads])

    train_error_summary = tf.summary.scalar("trainError", error)
    train_loss_summary = tf.summary.scalar("trainLoss", loss_op)
    train_summary_op = tf.summary.merge([train_error_summary, train_loss_summary, train_grad_summ_op])


    saver = tf.train.Saver(max_to_keep=0)
    sess = tf.Session()

    init = tf.global_variables_initializer()

    if(checkpoint_iter > 0): 
        saver.restore(sess, checkpoint_path + "/checkpoint-" + str(checkpoint_iter))
        

    
    sess.run(init)
    # op to write logs to Tensorboard
    writer = tf.summary.FileWriter(logs_path,
                                        graph=tf.get_default_graph())
    
    saver = tf.train.Saver(max_to_keep=0)
    # Training cycle

    i = 0 # counter

    for epoch in range(training_epochs):
    
        total_batch = int(mnist.train.num_examples / batch_size)
        # Loop over all batches
        for j in range(total_batch):
            data_x, data_y = mnist.train.next_batch(batch_size)
            print(i)
            sess.run(train, feed_dict={x: data_x, y: data_y})
            
            if(i % 2 == 0 and i > 0):
                # TEST IT
                test_x, test_y = mnist.train.next_batch(batch_size)
                writer.add_summary(
                    sess.run(test_summary_op,
                         feed_dict={x: test_x, y: test_y},
                        
                        ),
                i)
                writer.add_summary(
                    sess.run(train_summary_op,
                         feed_dict={x: data_x, y: data_y},
                        
                        ),
                i)
            
            if(i % save_every == 0 and i > 0):
                save_path = saver.save(sess,  checkpoint_path + "/checkpoint", global_step=i)
        
            i += 1 
                
                # print(np.argmax(test_y, 2)[0])
                # print(np.argmax(test_mask * sess.run(inference, feed_dict={batch_x: test_x, keep_prob: 1.0}), 2)[0])
            
            # Write logs at every iteration
            #summary_writer.add_summary(summary, epoch * total_batch + i)
            # Compute average loss
            #avg_cost += c / total_batch
        # Display logs per epoch step
        #if (epoch + 1) % display_step == 0:
        #    print("Epoch:", '%04d' % (epoch + 1), "cost=", "{:.9f}".format(avg_cost))


chaosGraphBaseline()
# baseline()

