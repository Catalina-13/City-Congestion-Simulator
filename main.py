# -*- coding: utf-8 -*-
"""
Created on Wed Jul 28 18:51:03 2021

@author: Catalina Negoita
"""

from preprocess import *
from model import *
import matplotlib
import matplotlib.pyplot as plt
from tensorflow import keras



# We parse the Data, or read directly from a pickle if we can
try:
    df = pd.read_pickle('geolife.pkl')
except:
    df = read_all_users('Data')

# We preprocess the dataframe, or read directly from a pickle if we can
try:
    df = pd.read_pickle('preprocessed.pkl')
except:
    df = preprocess(df)

df_train, df_test = div_fr(df)
x_train, y_train = df_to_data(df_train)
x_test, y_test = df_to_data(df_test)

#dense_model = dense_model(x_train.shape[1:], 100)
#train_model(dense_model, x_train, y_train, x_test, y_test, batch_size=32, epochs=1)


# Load model from file
model = keras.models.load_model('model1')

