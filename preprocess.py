# -*- coding: utf-8 -*-
"""
Created on Wed Jul 28 18:47:30 2021

@author: Catalina Negoita
"""

import numpy as np
import pandas as pd
import glob
import os.path
import datetime
import os

def read_plt(plt_file):
    points = pd.read_csv(plt_file, skiprows=6, header=None,
                         parse_dates=[[5, 6]], infer_datetime_format=True)

    # for clarity rename columns
    points.rename(inplace=True, columns={'5_6': 'time', 0: 'lat', 1: 'lon', 3: 'alt'})

    # remove unused columns
    points.drop(inplace=True, columns=[2, 4])

    return points

mode_names = ['walk', 'bike', 'bus', 'car', 'subway','train', 'airplane', 'boat', 'run', 'motorcycle', 'taxi']
mode_ids = {s : i + 1 for i, s in enumerate(mode_names)}

def read_labels(labels_file):
    labels = pd.read_csv(labels_file, skiprows=1, header=None,
                         parse_dates=[[0, 1], [2, 3]],
                         infer_datetime_format=True, delim_whitespace=True)

    # for clarity rename columns
    labels.columns = ['start_time', 'end_time', 'label']

    # replace 'label' column with integer encoding
    labels['label'] = [mode_ids[i] for i in labels['label']]

    return labels

def apply_labels(points, labels):
    indices = labels['start_time'].searchsorted(points['time'], side='right') - 1
    no_label = (indices < 0) | (points['time'].values >= labels['end_time'].iloc[indices].values)
    points['label'] = labels['label'].iloc[indices].values
    points['label'][no_label] = 0

def read_user(user_folder):
    labels = None

    plt_files = glob.glob(os.path.join(user_folder, 'Trajectory', '*.plt'))
    df = pd.concat([read_plt(f) for f in plt_files])

    labels_file = os.path.join(user_folder, 'labels.txt')
    if os.path.exists(labels_file):
        labels = read_labels(labels_file)
        apply_labels(df, labels)
    else:
        df['label'] = 0

    return df

def read_all_users(folder):
    subfolders = os.listdir(folder)
    dfs = []
    for i, sf in enumerate(subfolders):
        print('[%d/%d] processing user %s' % (i + 1, len(subfolders), sf))
        df = read_user(os.path.join(folder,sf))
        df['user'] = int(sf)
        dfs.append(df)
    return pd.concat(dfs)

def get_latitude(df):
    return df['lat'].to_numpy()

def get_longitude(df):
    return df['lon'].to_numpy()

def get_times(df):
    return df['time'].to_numpy()

def deltat(times):
    return np.diff(times) / np.timedelta64(1,'s')

def get_vel(latitude, longitude, dt):
    """
    input: a list of latitude and longitude coordinates 
           a list of deltatimes
    output:a list of velocities 
    """
    "Find distance between points "
    
    r=6371*(10**3)
    dlambda = np.diff(longitude)
    lat = latitude[1:]
    lat1 = latitude[:-1]
    
    distance_angulaire = np.arccos(np.sin(lat)*np.sin(lat1) + np.cos(lat)*np.cos(lat1)*np.cos(dlambda))
    vx = r*distance_angulaire
    vel = vx/dt
        
    return vel

def add_vel(df, latitude, longitude):
    time = get_times(df)
    dt = deltat(time)
    vel = get_vel(latitude, longitude, dt)
    df = df.iloc[1:]
    df.insert(4, "vel", vel, True)
    return df
    
def velpoints(df, lower, upper):
    return (df.loc[(df.vel > lower) & (df.vel < upper)])
    
def reshape_df(min_long, min_lat, mx_long, mx_lat, df):
    return (df.loc[(df.lat >= min_lat) & (df.lon >= min_long) & (df.lat <= mx_lat) & (df.lon <= mx_long)])
    
def div_fr(df):
    df_train = df.iloc [:-3000000]
    df_test = df.iloc [-3000000:]
    return df_train,df_test 
    
def preprocess(df):
    df = df.iloc[::2, :]
    latitude = get_latitude(df)
    longitude = get_longitude(df)
    df = add_vel(df, latitude, longitude)
    df = reshape_df(115.7945, 39.4669, 117.2461, 40.3424, df)
    df = velpoints(df, 0.1, 500.)
    df = df[(df['time'].dt.year != 2000)]
    return df
