# -*- coding: utf-8 -*-
"""Group Project.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1yp7lr2xYu4RM7Ks131rwdNxRXtCsCkL3
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import scipy

test_results = {}
url = 'http://archive.ics.uci.edu/ml/machine-learning-databases/autos/imports-85.data'

column_names = ['symboling', 'normalized-losse', 'make', 'fuel-type', 'aspiration',
                'doors','body-style','drive-wheels','engine-location','wheel-base','length','width','height',
                'curb-weight','engine-type','cylinders','engine-size','fuel-system',
                'bore','stroke','compression-ratio','horsepower','peak-rpm','city-mpg','highway-mpg','price']

raw_dataset = pd.read_csv(url, names=column_names,
                          na_values='?', comment='\t',
                          sep=',', skipinitialspace=True)

raw_dataset.shape

def plot_loss(history):
  plt.plot(history.history['loss'], label='loss')
  plt.plot(history.history['val_loss'], label='val_loss')
  plt.ylim([0, 40000])
  plt.xlabel('Epoch')
  plt.ylabel('Error [Price]')
  plt.legend()
  plt.grid(True)

def plot_horsepower(x, y):
  plt.scatter(train_features['horsepower'], train_labels, label='Data')
  plt.plot(x, y, color='k', label='Predictions')
  plt.xlabel('horsepower')
  plt.ylabel('price')
  plt.legend()

raw_dataset.head(3)

dataset = raw_dataset.copy()
dataset.pop('make')
dataset.pop('aspiration')
dataset.pop('normalized-losse')
dataset['doors']=dataset['doors'].map({'two':2,'four':4})
dataset['fuel-type']=dataset['fuel-type'].map({'diesel':1,'gas':2})
dataset['body-style']=dataset['body-style'].map({ 'hardtop':1, 'wagon':2, 'sedan':3, 'hatchback':4, 'convertible':5})
dataset['drive-wheels']=dataset['drive-wheels'].map({'4wd':1, 'fwd':2, 'rwd':3})
dataset['engine-location']=dataset['engine-location'].map({'front':1, 'rear':2})
dataset['engine-type']=dataset['engine-type'].map({'dohc':1, 'dohcv':2, 'l':3, 'ohc':4, 'ohcf':5, 'ohcv':6, 'rotor':7})
dataset['cylinders']=dataset['cylinders'].map({'eight':8, 'five':5, 'four':4, 'six':6, 'three':3, 'twelve':12, 'two':2})
dataset['fuel-system']=dataset['fuel-system'].map({'1bbl':1, '2bbl':2, '4bbl':3, 'idi':4, 'mfi':5, 'mpfi':6, 'spdi':7, 'spfi':8})
dataset

# dataset.pop('aspiration')
# dataset = dataset.pop

dataset.dropna().shape

dataset = dataset.dropna()
print(dataset.shape)
train_dataset = dataset.sample(frac=0.8, random_state=2)
print(train_dataset.shape)
test_dataset = dataset.drop(train_dataset.index)
sns.pairplot(train_dataset[['horsepower', 'peak-rpm', 'price', 'engine-size']], diag_kind='kde')
train_features = train_dataset.copy()
print(train_features.shape)
test_features = test_dataset.copy()
train_labels = train_features.pop('price')
test_labels = test_features.pop('price')
normalizer = tf.keras.layers.Normalization(axis=-1)
normalizer.adapt(np.array(train_features))
x = train_features['horsepower']
print(len(x))
y = train_labels
slope, intercept, r, p, se = scipy.stats.linregress(x, y)

train_features = train_dataset.copy()
# test_features = test_dataset.copy()
train_features.shape

train_labels

horsepower = np.array(train_features['horsepower'])
horsepower_normalizer = layers.Normalization(input_shape=[1,], axis=None)
horsepower_normalizer.adapt(horsepower)

horsepower_model = tf.keras.Sequential([ horsepower_normalizer ])
sample_output_from_untrained_model = horsepower_model.predict(train_features['horsepower'])
len(sample_output_from_untrained_model)

plt.hist(sample_output_from_untrained_model)

horsepower_model = tf.keras.Sequential([
    horsepower_normalizer,
    layers.Dense(units=1, use_bias=True, bias_initializer='ones')
])

horsepower_model.compile( 
    optimizer=tf.optimizers.Adam(learning_rate=150),
    loss='mean_absolute_error')

train_features.shape

history = horsepower_model.fit(
    train_features['horsepower'], # X (horspower)
    train_labels, # Y (price)
    # idea: y = f(x)
    epochs=125, # how many rounds you want to train your neural networks
    # Suppress logging.
    batch_size=128,
    verbose=1,
    # Calculate validation results on 5% of the training data.
    validation_split = 0.05
    )
#plot_loss(history)
hist = pd.DataFrame(history.history)
hist['epoch'] = history.epoch
test_results['horsepower_model'] = horsepower_model.evaluate(
    test_features['horsepower'],
    test_labels, verbose=0)
x = tf.linspace(0.0, 250, 251)
y = horsepower_model.predict(x)
plot_horsepower(x, y)

linear_model = tf.keras.Sequential([
    normalizer,
    layers.Dense(units=1, use_bias=True, bias_initializer='ones')
])
linear_model.compile(
    optimizer=tf.optimizers.Adam(learning_rate=150),
    loss='mean_absolute_error')
history = linear_model.fit(
    train_features,
    train_labels,
    epochs=175,
    # Suppress logging.
    verbose=1,
    batch_size=128,
    validation_split = 0.05)
plot_loss(history)
test_results['linear_model'] = linear_model.evaluate(
    test_features, test_labels, verbose=0)

def build_and_compile_model(norm):
  model = keras.Sequential([
      norm,
      layers.Dense(64, activation='relu'),
      layers.Dense(64, activation='relu'),
      layers.Dense(units=1, use_bias=True, bias_initializer='ones')
  ])

  model.compile(loss='mean_absolute_error',
                optimizer=tf.keras.optimizers.Adam(.15))
  return model

dnn_horsepower_model = build_and_compile_model(horsepower_normalizer)
dnn_horsepower_model.summary()
history = dnn_horsepower_model.fit(
    train_features['horsepower'],
    train_labels,
    batch_size=128,
    validation_split=0.05,
    verbose=1, epochs=70)
#plot_loss(history)

x = tf.linspace(0.0, 250, 251)
y = dnn_horsepower_model.predict(x)
plot_horsepower(x, y)
test_results['dnn_horsepower_model'] = dnn_horsepower_model.evaluate(
    test_features['horsepower'], test_labels,
    verbose=0)

dnn_model = build_and_compile_model(normalizer)
dnn_model.summary()
history = dnn_model.fit(
    train_features,
    train_labels,
    validation_split=0.2,
    verbose=1, epochs=13)
plot_loss(history)
test_results['dnn_model'] = dnn_model.evaluate(test_features, test_labels, verbose=0)
pd.DataFrame(test_results, index=['Mean absolute error [Price]']).T

test_predictions = dnn_model.predict(test_features).flatten()

a = plt.axes(aspect='equal')
plt.scatter(test_labels, test_predictions)
plt.xlabel('True Values [Price]')
plt.ylabel('Predictions [Price]')
lims = [0, 50]
plt.xlim(lims)
plt.ylim(lims)
_ = plt.plot(lims, lims)

error = test_predictions - test_labels
plt.hist(error, bins=25)
plt.xlabel('Prediction Error [MPG]')
_ = plt.ylabel('Count')
dnn_model.save('dnn_model')
reloaded = tf.keras.models.load_model('dnn_model')

test_results['reloaded'] = reloaded.evaluate(
    test_features, test_labels, verbose=0)
pd.DataFrame(test_results, index=['Mean absolute error [MPG]']).T