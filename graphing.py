# -*- coding: utf-8 -*-
"""
Created on Wed Jul 28 18:51:38 2021

@author: Catalina Negoita
"""

import numpy as np 
import matplotlib.image as mpimg
import matplotlib.pyplot as plt

def img_matrix(list_matrix):
    beijing_img=mpimg.imread('Beijing_map.png')    
    
    for j in range(len(list_matrix)):
        plt.imshow(list_matrix[j], cmap='jet', interpolation='nearest')
        plt.imshow(beijing_img, extent=[115.7945, 117.2461, 39.4669, 40.3424], alpha=0.5)
        plt.ylabel("Latitude", fontsize=14)
        plt.xlabel("Longitude", fontsize=14)
        nom='photo-matrix-{number}.png'.format(number = j)
        plt.savefig(nom, dpi=200)
