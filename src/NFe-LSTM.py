import pandas as pd
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import numpy as np
import re
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Activation
from tensorflow.keras.layers import LSTM
from tensorflow.keras.optimizers import Adam
from tensorflow.keras import layers
from tensorflow.keras import losses
from tensorflow.keras import preprocessing
from tensorflow.keras.layers.experimental.preprocessing import TextVectorization
import tensorflow_text as tf_text

BUFFER_SIZE = 10000
BATCH_SIZE = 64
VOCAB_SIZE = 10000

def generate_data():
    data = pd.read_excel('../database/BaseTrabIA1.xlsx')
    df = pd.DataFrame(columns=['Text', 'Label'])
    data = data[(data['NCM'] == 33049910) | (data['NCM'] == 33072010)]
    df['Text']  = data['DESCRIÇÃO (NFe)']
    df['Label'] = data['NCM'].replace({33049910: 0, 33072010: 1})
    df['Text'] = df['Text'].str.lower().replace('\W',' ', regex=True)
    train = pd.DataFrame(columns=['Text', 'Label'])
    test = pd.DataFrame(columns=['Text', 'Label'])
    train['Text'], test['Text'], train['Label'], test['Label'] = train_test_split(df['Text'], df['Label'], random_state=42, shuffle=True, test_size=0.3)
    train_dataset = tf.data.Dataset.from_tensor_slices((train['Text'].values, train['Label'].values))
    test_dataset = tf.data.Dataset.from_tensor_slices((test['Text'].values, test['Label'].values))
    """for text, label in train_dataset.take(10):
        print ('Text: {}, Label: {}'.format(text, label))
    for text, label in test_dataset.take(10):
        print ('Text: {}, Label: {}'.format(text, label))"""

    return train_dataset, test_dataset

def plot_graphs(history, metric):
    plt.plot(history.history[metric])
    plt.plot(history.history['val_'+metric], '')
    plt.xlabel("Epochs")
    plt.ylabel(metric)
    plt.legend([metric, 'val_'+metric])
    plt.show()


def LSTM_model(train_dataset, test_dataset, encoder):
    model = tf.keras.Sequential([
    encoder,
    tf.keras.layers.Embedding(len(encoder.get_vocabulary()), 64, mask_zero=True),
    tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(64,  return_sequences=True)),
    tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(32)),
    tf.keras.layers.Dense(64, activation='linear'),
    tf.keras.layers.Dropout(0.5),
    tf.keras.layers.Dense(1)])


    model.compile(loss=tf.keras.losses.BinaryCrossentropy(from_logits=True),
              optimizer='adam',
              metrics=['accuracy'])
    history = model.fit(train_dataset, epochs=3,
                    validation_data=test_dataset, 
                    validation_steps=30)
    test_loss, test_acc = model.evaluate(test_dataset)

    print('Test Loss: {}'.format(test_loss))
    print('Test Accuracy: {}'.format(test_acc))

    plt.figure(figsize=(16,8))
    plot_graphs(history, 'accuracy')
    plot_graphs(history, 'loss')

def main():
    train_dataset, test_dataset = generate_data()
    train_dataset = train_dataset.shuffle(BUFFER_SIZE).batch(BATCH_SIZE).prefetch(tf.data.AUTOTUNE)
    test_dataset = test_dataset.batch(BATCH_SIZE).prefetch(tf.data.AUTOTUNE)
    encoder = tf.keras.layers.experimental.preprocessing.TextVectorization(max_tokens=VOCAB_SIZE)
    encoder.adapt(train_dataset.map(lambda text, label: text))
    vocab = np.array(encoder.get_vocabulary())
    #print(vocab[:20])
    LSTM_model(train_dataset, test_dataset, encoder)

if __name__ == '__main__':
    main()