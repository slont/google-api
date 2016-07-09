# coding: utf-8

from pymongo import MongoClient


class MongoUtil(object):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "__instance__"):
            cls.__instance__ = super(MongoUtil, cls).__new__(cls, *args)
            print('connect mongo.')
            cls.__client = MongoClient('localhost', 27017)
        return cls.__instance__

    def __init__(self):
        pass

    @classmethod
    def create_col(cls, db_name, col_names):
        print('{} db create start.'.format(db_name))
        db = cls.__client[db_name]
        li = []
        for name in col_names:
            li.append(db[name])
        return tuple(li) if 1 < len(li) else li[0]
