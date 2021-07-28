# -*- coding: utf-8 -*-
"""
Created on Wed Jul 28 18:52:19 2021

@author: Catalina Negoita
"""

from typing import Union
import abc


class Graph(abc.ABC):
    @abc.abstractmethod
    def set_vertex(self, n: int, v: object) -> None:
        pass

    @abc.abstractmethod
    def get_vertex(self, n: int) -> Union[object, None]:
        pass

    @abc.abstractmethod
    def has_vertex(self, n: int) -> bool:
        pass

    @abc.abstractmethod
    def get_vertices(self) -> list[int]:
        pass

    @abc.abstractmethod
    def get_neighbors(self, n: int) -> list[int]:
        pass

    @abc.abstractmethod
    def set_edge(self, a: int, b: int, value: object) -> None:
        pass

    @abc.abstractmethod
    def get_edge(self, a: int, b: int) -> Union[object, None]:
        pass

    @abc.abstractmethod
    def has_edge(self, a: int, b: int) -> bool:
        pass

    @abc.abstractmethod
    def delete_edge(self, a: int, b: int) -> None:
        pass

    @abc.abstractmethod
    def delete_vertex(self, n: int) -> None:
        pass

    @abc.abstractmethod
    def to_buffer(self) -> list[int]:
        pass

    @classmethod
    @abc.abstractmethod
    def from_buffer(cls, b: str, ptr: int = 0, imports: list[type] = []) -> 'Graph':
        pass

    def to_file(self, filename: str) -> None:
        with open(filename, "wb") as h:
            h.write(bytes(self.to_buffer()))

    @classmethod
    def from_file(cls, filename: str, imports: list[type] = []) -> 'Graph':
        with open(filename, "rb") as h:
            s = h.read()
        return cls.from_buffer(s, imports=imports)

    def vertex_count(self) -> int:
        return len(self.get_vertices())

    def edge_count(self) -> int:
        return sum([len([x for x in self.get_neighbors(a) if x > a]) for a in self.get_vertices()])


class DirectionalGraph(Graph):
    def __init__(self, d: Union[dict[int, dict[int, object]], None] = None, v: Union[dict[int, object], None] = None):
        self.__dict = d if d is not None else {}
        self.__vdata = v if v is not None else {}

    def set_vertex(self, n: int, v: object) -> None:
        self.__dict[n] = {}
        self.__vdata[n] = v

    def get_vertex(self, n: int) -> object:
        return self.__vdata.get(n)

    def has_vertex(self, n: int) -> bool:
        return n in self.__dict

    def get_vertices(self) -> list[int]:
        return [x[0] for x in self.__dict.items()]

    def get_neighbors(self, n: int) -> list[int]:
        self.check_has_vertex(n)
        return [x[0] for x in self.__dict[n].items()]

    def check_has_vertex(self, n: int) -> None:
        if not self.has_vertex(n):
            raise Exception("Vertex %d does not exist" % n)

    def set_edge(self, a: int, b: int, value: object) -> None:
        self.check_has_vertex(a)
        self.check_has_vertex(b)
        self.__dict[a][b] = value

    def get_edge(self, a: int, b: int) -> Union[object, None]:
        self.check_has_vertex(a)
        self.check_has_vertex(b)
        return self.__dict[a].get(b)

    def has_edge(self, a: int, b: int) -> bool:
        return b in self.__dict[a]

    def delete_edge(self, a: int, b: int) -> None:
        self.check_has_vertex(a)
        self.check_has_vertex(b)
        del (self.__dict[a])[b]

    def delete_vertex(self, n: int) -> None:
        del self.__dict[n]
        for _, d in self.__dict.items():
            if n in d: del d[n]

    def to_buffer(self) -> str:
        res = ""

        def write_bytes(b):
            nonlocal res
            for byte in b:
                res += chr(byte)

        def write_int(n):
            write_bytes(n.to_bytes(8, byteorder="big"))

        def write_string(s):
            nonlocal res
            write_int(len(s))
            res += s

        write_int(len(self.__dict))

        for a, d in self.__dict.items():
            write_int(a)
            write_string(repr(self.__vdata[a]))
            write_int(len(d))
            for b, val in d.items():
                write_int(b)
                write_string(repr(val))

        return res

    @classmethod
    def from_buffer(cls, b: str, ptr: int = 0, imports: list[type] = []) -> 'DirectionalGraph':
        for i in imports:
            globals()[i.__name__] = i
        def read_bytes(n):
            result = []
            nonlocal b, ptr
            for i in range(n):
                result.append(ord(b[i + ptr]))
            ptr += n
            return result

        def read_int():
            return int.from_bytes(read_bytes(8), byteorder="big")

        def read_string():
            length = read_int()
            bs = read_bytes(length)
            res = ""
            for i in range(length):
                res += chr(bs[i])
            return res

        d = {}
        v = {}
        vertices_count = read_int()
        for _ in range(vertices_count):
            a = read_int()
            d[a] = {}
            v[a] = eval(read_string())
            edges_count = read_int()
            for _ in range(edges_count):
                bn = read_int()
                s = read_string()
                obj = eval(s)
                d[a][bn] = obj

        return DirectionalGraph(d, v)

    def __str__(self):
        res = "DirectionalGraph:\n"
        for a, d in self.__dict.items():
            res += "  vertex %d:\n" % a
            for b, val in d.items():
                res += "    edge to %d: %s\n" % (b, str(val))
        return res


class BidirectionalGraph(Graph):
    def __init__(self, d: Union[dict[int, dict[int, object]], None] = None, v: Union[dict[int, object], None] = None):
        self.__dict = d if d is not None else {}
        self.__vdata = v if v is not None else {}

    def order(self, a, b):
        if a < b: return a, b
        else: return b, a

    def set_vertex(self, n: int, v: object) -> None:
        self.__dict[n] = {}
        self.__vdata[n] = v

    def get_vertex(self, n: int) -> object:
        return self.__vdata.get(n)

    def has_vertex(self, n: int) -> bool:
        return n in self.__dict

    def get_vertices(self) -> list[int]:
        return list(self.__dict.keys())

    def get_neighbors(self, n: int) -> list[int]:
        self.check_has_vertex(n)
        return list(self.__dict[n].keys())

    def check_has_vertex(self, n: int) -> None:
        if not self.has_vertex(n):
            raise Exception("Vertex %d does not exist" % n)

    def set_edge(self, a: int, b: int, value: object) -> None:
        self.check_has_vertex(a)
        self.check_has_vertex(b)
        self.__dict[a][b] = value
        self.__dict[b][a] = value

    def get_edge(self, a: int, b: int) -> Union[object, None]:
        self.check_has_vertex(a)
        self.check_has_vertex(b)
        return self.__dict[a].get(b)

    def has_edge(self, a: int, b: int) -> bool:
        return b in self.__dict[a]

    def delete_edge(self, a: int, b: int) -> None:
        self.check_has_vertex(a)
        self.check_has_vertex(b)
        del (self.__dict[a])[b]
        del (self.__dict[b])[a]

    def delete_vertex(self, n: int) -> None:
        del self.__dict[n]
        for _, d in self.__dict.items():
            if n in d: del d[n]

    def to_buffer(self) -> list[int]:
        res = []

        def write_bytes(b):
            nonlocal res
            res += b

        def write_int(n):
            write_bytes(n.to_bytes(8, byteorder="big"))

        def write_string(s):
            nonlocal res
            write_int(len(s))
            res += bytes(s, encoding="utf8")

        write_int(len(self.__dict))

        for a, _ in self.__dict.items():
            d = self.get_neighbors(a)
            write_int(a)
            s = repr(self.__vdata[a])
            write_string(s)
            write_int(len([x for x in d if x > a]))
            for b in d:
                if a < b:
                    write_int(b)
                    write_string(repr(self.get_edge(a, b)))

        return res

    @classmethod
    def from_buffer(cls, b: list[int], ptr: int = 0, imports: list[type] = []) -> 'BidirectionalGraph':
        for i in imports:
            globals()[i.__name__] = i
        def read_bytes(n):
            nonlocal b, ptr
            ptr += n
            return b[ptr-n:ptr]

        def read_int():
            return int.from_bytes(read_bytes(8), byteorder="big")

        def read_string():
            length = read_int()
            bs = read_bytes(length)
            res = ""
            for i in range(length):
                res += chr(bs[i])
            return res

        g = BidirectionalGraph()
        vertices_count = read_int()
        for _ in range(vertices_count):
            a = read_int()
            g.set_vertex(a, eval(read_string()))
            edges_count = read_int()
            for _ in range(edges_count):
                bn = read_int()
                if not g.has_vertex(bn):
                    g.set_vertex(bn, None)
                s = read_string()
                obj = eval(s)
                g.set_edge(a, bn, obj)

        return g

    def __str__(self):
        res = "BidirectionalGraph:\n"
        for a, d in self.__dict.items():
            res += "  vertex %d:\n" % a
            for b, val in d.items():
                res += "    edge to %d: %s\n" % (b, str(val))
        return res
