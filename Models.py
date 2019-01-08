# -*- coding:utf-8 -*-

import datetime
from flask_login import UserMixin

users = []


def get_user(user_id):
    for user in users:
        if user.get_id() == user_id:
            return user


class User(UserMixin):
    def __new__(cls, user_id, username, password):
        self = object.__new__(cls)
        self._user_id = user_id
        self._username = username
        self._password = password
        self._join_time = datetime.datetime.now
        # 这个append操作需要替换为添加到数据库
        users.append(self)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self._user_id

    def get_username(self):
        return self._username

    @classmethod
    def create_user(cls, username, password):
        cls(len(users), username, password)
        return cls


class Post():
    pass


class Relation():
    pass
