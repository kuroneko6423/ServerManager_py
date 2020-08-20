#!/usr/bin/env python
# -*- coding: utf-8 -*-

class DateBase:
    def __init__(self, name=__name__):
        self.db = {}

    def get(self, path):
        pass

    def set(self, path, value):
        pass

    def save(self):
        pass

    def __parse_path(self, path):
        path = path.split(".")
        r = self.db
        for x in path:
            if r[x] == None:
                return None
            r = r[x]
        return r

def parse_path(path,db):
    path = path.split(".")
    r = db
    for x in path:
        if type(r[x]) is dict:
            return None
        r = r[x]
    return r