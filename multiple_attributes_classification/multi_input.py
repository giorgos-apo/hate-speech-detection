from string import punctuation

import numpy as np
import pandas as pd
from gensim.parsing.preprocessing import STOPWORDS
from keras_preprocessing.sequence import pad_sequences
from keras_preprocessing.text import Tokenizer
from sklearn.model_selection import train_test_split
from tensorflow.keras.layers import Embedding, Dense, Flatten, Input, LSTM, Concatenate
from tensorflow.keras.models import Model, Sequential
from tensorflow.keras.utils import plot_model
from tensorflow.keras.optimizers import Adam
import matplotlib.pyplot as plt

from preprocess_twitter import tokenize as tokenizer_g

# the following two lines are used to create the plot of the neural network model
import os
os.environ["PATH"] += os.pathsep + 'C:\\Program Files\\Graphviz\\bin'


# vectors dimension for the embedding
EMBEDDING_DIM = 50
# validation data size (i.e 0.2 = 20%)
VALIDATION_SIZE = 0.2
# epochs to train the neural network
EPOCHS = 10


def tokenize(tweet):
    return tokenizer_g(tweet)


def split_and_remove_punctuation_and_stopwords(tweet):
    text = ''.join([c for c in tweet if c not in punctuation])
    words = text.split()
    words = [word for word in words if word not in STOPWORDS]
    return words


############################
# MAIN APP
############################

# Preparing the text data
df = pd.read_csv("../dataset/tweet_user_data_final.csv")

# df = df[["tweet_text", "is_hate"]]

df["tweet_text"] = df["tweet_text"].apply(tokenize).apply(split_and_remove_punctuation_and_stopwords)

text = df["tweet_text"]

# let's use Keras.Tokenizer to convert our sentences to vectors
token = Tokenizer()

token.fit_on_texts(text)

vocab_size = len(token.word_index) + 1

# converts text to sequence of vocab index (i.e [3, 5, 11, 1, 9, 7])
encoded_text = token.texts_to_sequences(text)

# get max length of sentences in corpus to create padded sentences of this length
max_length = len(max(encoded_text, key=len))

padded_text = pad_sequences(encoded_text, maxlen=max_length, padding="post")

# Textual input for the first model in vector shape (i.e [23,1,11,13,5,9])
X1 = padded_text

# Features for the second model
X2 = np.array(df[["user_total_tweets"]])

y = df["is_hate"]


######### GLOVE VECTORS
GLOVE_FILE = "C:\\Users\\giorg\\Documents\\Thesis\\GloveModelFile\\glove.twitter.27B."+str(EMBEDDING_DIM)+"d.txt"

glove_vectors = dict()

file = open(GLOVE_FILE, encoding="utf-8")

for line in file:
    values = line.split()
    word = values[0]
    vectors = np.asarray(values[1:])
    glove_vectors[word] = vectors
file.close()

word_vector_matrix = np.zeros((vocab_size, EMBEDDING_DIM))

for word, index in token.word_index.items():
    vector = glove_vectors.get(word)
    if vector is not None:
        word_vector_matrix[index] = vector


########## MODELS
input_1 = Input(shape=(max_length,))
input_2 = Input(shape=(1,))

vector_size = EMBEDDING_DIM

# get the output from the first submodel
embedding_layer = Embedding(vocab_size, vector_size, weights=[word_vector_matrix])(input_1)
LSTM_layer_1 = LSTM(128)(embedding_layer)

# get the output from the second submodel
dense_layer_1 = Dense(10, activation='relu')(input_2)
dense_layer_2 = Dense(10, activation='relu')(dense_layer_1)

# concatenate the two outputs
concat_layer = Concatenate()([LSTM_layer_1, dense_layer_2])

# build final model
dense_layer_3 = Dense(10, activation="relu")(concat_layer)
output = Dense(1, activation="sigmoid")(dense_layer_3)
model = Model(inputs=[input_1, input_2], outputs=output)

model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['acc'])

#plot_model(model, to_file='model_plot3.png', show_shapes=True, show_layer_names=True)

########### MODEL BUILDING
# X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42, test_size=0.2, stratify=y)
#
# # we will split the training data in valuation dataset
# val_size = int(len(X_train)*VALIDATION_SIZE)
# X_val = X_train[:val_size]
# X_train_partial = X_train[val_size:]
# y_val = y_train[:val_size]
# y_train_partial = y_train[val_size:]
#

#
# # Sequential Model
# model = Sequential()
# # use this for custom embeddings
# # model.add(Embedding(vocab_size, vector_size, input_length=max_length))
# # or use this to enable GloVe pretrained embeddings
# model.add(Embedding(vocab_size, vector_size, input_length=max_length, weights=[word_vector_matrix]))
# model.add(Flatten())
# model.add(Dense(1, activation="sigmoid"))
#
# model.compile(optimizer=Adam(learning_rate=0.001), loss="binary_crossentropy", metrics=["accuracy"])
#
# class_weight = {
#     0: 1,
#     1: 5
# }
# clf = model.fit(X_train_partial, y_train_partial, epochs=EPOCHS, verbose=1, validation_data=(X_val, y_val), class_weight=class_weight)
#
# loss, accuracy = model.evaluate(X_test, y_test, verbose=0)
# print('Accuracy: %f' % (accuracy*100))
