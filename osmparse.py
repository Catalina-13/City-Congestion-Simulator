# -*- coding: utf-8 -*-
"""
Created on Wed Jul 28 18:48:17 2021

@author: Catalina Negoita
"""

import xml.etree.ElementTree as et
from dataclasses import dataclass
from graph import DirectionalGraph, BidirectionalGraph
from math import *


@dataclass(repr=False)
class Node:
    id: int
    lat: float
    long: float

    def __repr__(self):
        return "Node(%d,%f,%f)" % (self.id, self.lat, self.long)


@dataclass
class Road:
    type: str
    length: float

    def __repr__(self):
        return "Road(%s,%f)" % (repr(self.type), self.length)


class OSMParser:
    def __init__(self):
        pass

    def parse(self, osm: str) -> BidirectionalGraph:
        def getattrs(node):
            res = {}
            for e in node:
                if e.tag == "tag":
                    res[e.attrib["k"]] = e.attrib["v"]
            return res

        root = et.fromstring(osm)
        nodes = {}
        result = BidirectionalGraph()
        for e in root:
            if e.tag == "node":
                id = int(e.attrib["id"])
                nodes[id] = Node(id, float(e.attrib["lat"]), float(e.attrib["lon"]))
            elif e.tag == "way":
                attr = getattrs(e)
                if attr.get("area") == "yes": continue
                if attr.get("building") == "yes": continue
                if attr.get("highway") not in ["primary", "secondary"]: continue
                nds = [x for x in e if x.tag == "nd" and int(x.attrib["ref"]) in nodes]
                if len(nds) < 2: continue
                for nd in nds:
                    id = int(nd.attrib["ref"])
                    node = nodes[id]
                    if not result.has_vertex(id):
                        result.set_vertex(id, node)
                for i in range(1, len(nds)):
                    result.set_edge(
                        int(nds[i-1].attrib["ref"]),
                        int(nds[i].attrib["ref"]),
                        Road(attr.get("highway"), -1.0)
                    )

        def haversine(lon1, lat1, lon2, lat2):
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

        for a in result.get_vertices():
            for b in result.get_neighbors(a):
                road = result.get_edge(a, b)
                node1 = result.get_vertex(a)
                node2 = result.get_vertex(b)
                road.length = haversine(node1.long, node1.lat, node2.long, node2.lat)
        return result
