# -*- coding: utf-8 -*-
"""
Created on Wed Jul 28 18:49:28 2021

@author: Catalina Negoita
"""

import tensorflow as tf
from tensorflow import keras
import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.layers import Dense, Flatten, Activation
from tensorflow.keras.layers import Conv2D, MaxPooling2D
from tensorflow.keras.layers import Dropout, BatchNormalization
from tensorflow.keras.optimizers import SGD
import pandas as pd
import datetime


def df_to_x(df):
    times =  df['time'].dt.time
    times = times.apply(lambda x: x.hour * 3600 + x.minute*60 + x.second)
    days = df['time'].dt.dayofweek
    hot_days = np.zeros((days.size, 7))
    hot_days[np.arange(days.size),days] = 1
    times = times/86400
    times = times.to_numpy()
    x = np.column_stack([times, hot_days])
    return x

def df_to_y(df):
    y = np.zeros((len(df),10, 10))
    coords = df[['lat', 'lon']]
    coords['lat'] = coords['lat'].apply(lambda x: int(((x-39.470543)/0.871857) * 10))
    coords['lon'] = coords['lon'].apply(lambda x: int(((x-115.7946)/1.449734) * 10))
    indices = coords.to_numpy()
    indices = np.column_stack([np.arange(len(df)), indices])
    for index in indices:
        y[index[0], index[1], index[2]] = 1
    return y.reshape((len(df), 100))

def df_to_data(df):
    return df_to_x(df), df_to_y(df)

def train_model(model, x, y, x_test, y_test, batch_size=32, epochs=10, file_name=None):
    """
    Trains the model on the given data.
    """
    callback = tf.keras.callbacks.EarlyStopping(monitor='val_accuracy', patience=2)
    model.fit(x, y, batch_size, epochs, callbacks=[callback], validation_data=(x_test, y_test))

def dense_model(input_shape, num_cells):
    """
    Returns a compiled keras Sequential model
    
    :param input_shape: shape of ONE example as passed to the first layer
    :param num_classes: number of output classes as passed to the last layer
    """
    model = tf.keras.Sequential()
    
    model.add(Flatten(input_shape=input_shape))
    
    model.add(Dense(2048, activation='relu'))
    model.add(BatchNormalization())

    model.add(Dense(1024, activation='relu'))
    model.add(BatchNormalization())
    
    model.add(Dense(512, activation='relu'))
    model.add(BatchNormalization())
    
    model.add(Dense(256, activation='relu'))
    model.add(BatchNormalization())
    
    model.add(Dense(num_cells, activation='sigmoid'))
    
    model.compile(loss='categorical_crossentropy', 
    optimizer="SGD", 
    metrics=['accuracy'])
    
    return model

def cnn_model(input_shape, num_cells):

    model = tf.keras.Sequential()
    model.add(Conv2D(32, (3, 3),input_shape=input_shape))
    model.add(Activation(tf.keras.activations.relu))
    
    model.add(Conv2D(32, (3, 3)))
    model.add(Activation(tf.keras.activations.relu))
    
    model.add(Dropout(0.25))
    model.add(BatchNormalization())
    model.add(MaxPooling2D((2, 2)))
    model.add(Conv2D(64, (3, 3)))
    model.add(Activation(tf.keras.activations.relu))
    
    model.add(Conv2D(64, (3, 3)))
    model.add(Activation(tf.keras.activations.relu))
    
    model.add(Dropout(0.25))
    model.add(BatchNormalization())
    model.add(MaxPooling2D((2, 2)))
    
    model.add(Flatten())
    model.add(Dense(512, activation='relu'))
    
    model.add(Dropout(0.25))
    model.add(BatchNormalization())
    model.add(Dense(num_cells, activation='sigmoid'))

    model.compile(loss='categorical_crossentropy', 
    optimizer="SGD", 
    metrics=['accuracy'])

    return(model)
