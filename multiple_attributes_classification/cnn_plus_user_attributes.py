from tensorflow.keras.optimizers import Adam
from tensorflow.keras.utils import plot_model

import classification_config as clf_config
import prepare_data as data
from glove_producer import produce_glove_vector_matrix

from tensorflow.keras.layers import Embedding, Dense, Input, Conv1D, MaxPooling1D, Flatten, Concatenate
from tensorflow.keras.models import Model

# the following two lines are used to create the plot of the neural network model
import os
os.environ["PATH"] += os.pathsep + 'C:\\Program Files\\Graphviz\\bin'

# GLOVE VECTORS
word_vector_matrix = produce_glove_vector_matrix(clf_config.EMBEDDING_DIM, data.vocab_size, data.token)

# MODELS
input_1 = Input(shape=(data.max_length,))
input_2 = Input(shape=(data.user_attributes_count,))

# get the output from the first submodel
embedding_layer = Embedding(data.vocab_size, clf_config.EMBEDDING_DIM, weights=[word_vector_matrix])(input_1)
conv1d_layer = Conv1D(filters=64, kernel_size=5, activation="relu")(embedding_layer)
max_pooling_layer = MaxPooling1D(pool_size=5)(conv1d_layer)
flatten_layer = Flatten()(max_pooling_layer)
dense_text_layer = Dense(8, activation="relu")(flatten_layer)

# get the output from the second submodel
dense_layer_1 = Dense(8, activation='sigmoid')(input_2)
dense_layer_2 = Dense(8, activation='sigmoid')(dense_layer_1)

# concatenate the two outputs
concat_layer = Concatenate()([dense_text_layer, dense_layer_2])

# construct output layer
dense_layer_3 = Dense(4, activation="sigmoid")(concat_layer)
output = Dense(1, activation="sigmoid")(dense_layer_3)

# build final model
model = Model(inputs=[input_1, input_2], outputs=output)

# prepare the model
model.compile(optimizer=Adam(learning_rate=0.001), loss='binary_crossentropy', metrics=['acc'])

# plot the model
plot_model(model, to_file='../nn_plots/cnn_plus_user_attr/model_plot.png', show_shapes=True, show_layer_names=True)

# train the model
model.fit(x=[data.X_train_text, data.X_train_user], y=data.y_train, epochs=clf_config.EPOCHS, validation_split=clf_config.VALIDATION_SIZE)

# evaluate the model on the test dataset
loss, accuracy = model.evaluate(x=[data.X_test_text, data.X_test_user], y=data.y_test, verbose=0)
print('Accuracy: %f' % (accuracy*100))