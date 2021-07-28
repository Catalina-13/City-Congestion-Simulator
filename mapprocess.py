# -*- coding: utf-8 -*-
"""
Created on Wed Jul 28 18:50:21 2021

@author: Catalina Negoita
"""

from graph import *
from osmparse import Road
import sys
from math import *
import matplotlib.pyplot as plt


def optimize_roads(g: Graph):
    v = g.get_vertices()
    c = 0
    for i in range(len(v)):
        print("%d/%d, optimized %d" % (i, len(v), c))
        a = v[i]
        n = g.get_neighbors(a)
        if len(n) != 2 and len(n) != 0: continue
        if len(n) != 0 and g.has_edge(n[0], n[1]): continue
        c += 1
        if len(n) == 0: g.delete_vertex(a); continue
        r1, r2 = g.get_edge(n[0], a), g.get_edge(a, n[0])
        r = Road("mixed" if r1.type != r2.type else r1.type, r1.length + r2.length)
        g.delete_vertex(a)
        g.set_edge(n[0], n[1], r)


def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    # Radius of earth in kilometers is 6371
    m = 6371000 * c
    return m


#                                                            (score,   lat,  long)
def calculate_congestion(g: BidirectionalGraph, points: list[(float, float, float)]):
    for v in g.get_vertices():
        node = g.get_vertex(v)
        setattr(node, "congestion", 70000 * sum([p[0] / haversine(p[1], p[2], node.lat, node.long) for p in points]) / len(points))

    for a in g.get_vertices():
        for b in g.get_neighbors(a):
            if a < b:
                setattr(g.get_edge(a, b), "congestion", (g.get_vertex(a).congestion + g.get_vertex(b).congestion) / 2)


def calculate_congestion_matrix(g: BidirectionalGraph, m: list[list[float]], lat1, long1, lat2, long2):
    height = len(m)
    width = len(m[0])
    for v in g.get_vertices():
        node = g.get_vertex(v)
        if node.lat < lat1 or node.lat > lat2 or node.long < long1 or node.long > long2:
            setattr(node, "congestion", 0)
            continue
        ik, i = modf((node.lat - lat1) / (lat2 - lat1) * height)
        jk, j = modf((node.long - long1) / (long2 - long1) * width)
        i, j = int(i), int(j)
        topleft = m[i][j]
        topright = 0 if j+1 == width else m[i][j+1]
        bottomleft = 0 if i+1 == height else m[i+1][j]
        bottomright = 0 if i+1 == height or j+1 == width else m[i+1][j+1]
        c = 0
        c += topleft * (1-ik) * (1-jk) + topright * (1-ik) * jk
        c += bottomleft * ik * (1-jk) + bottomright * ik * jk

        setattr(node, "congestion", c)

    for a in g.get_vertices():
        for b in g.get_neighbors(a):
            if a < b:
                setattr(g.get_edge(a, b), "congestion", (g.get_vertex(a).congestion + g.get_vertex(b).congestion) / 2)


def output_to_points(matrix, lat1, long1, lat2, long2):
    height = len(matrix)
    width = len(matrix[0])
    result = []
    for i in range(height):
        for j in range(width):
            result.append(
                (matrix[i][j], lat1 + (lat2 - lat1) * (i + 0.5) / height, long1 + (long2 - long1) * (j + 0.5) / width)
            )
    return result


def plot(g: BidirectionalGraph, f: Union[str, None] = None):
    for a in g.get_vertices():
        for b in g.get_neighbors(a):
            if a < b:
                n1 = g.get_vertex(a)
                n2 = g.get_vertex(b)
                c = min(g.get_edge(a, b).congestion, 1)
                plt.plot([n1.long, n2.long], [n1.lat, n2.lat], color=(c, 1-c, 0))


    plt.xlabel('longitude')
    plt.ylabel('latitude')

    if f is None:
        plt.show()
    else:
        plt.savefig(f)
