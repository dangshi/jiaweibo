# -*- coding:utf-8 -*-

import datetime
from flask_login import UserMixin

users = []

def get_user(user_id):
    for user in users:
        if user.get_id() == user_id:
            return user
def get_user_by_name(name):
    for user in users:
        if user.get_username() == name:
            return user


class User(UserMixin):
    def __init__(self, user_id, username, password="", post_num=0, following_num = 0, followed_num=0, following=[], followed=[]):
        # self = object.__new__(cls)
        self._user_id = user_id
        self._username = username
        self._password = password
        self._join_time = datetime.datetime.now
        if password:
            users.append(self)
        self.post_num = post_num
        self.following_num = following_num
        self.followed_num = followed_num
        self.following = following
        self.followed = followed

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

    # @classmethod
    # def create_user(cls,userid, username, password):
    #     cls(userid, username, password)
    #     return cls

    def get_followers(self):
        return self.followed

    def get_following(self):
        return self.following

class Post():
    def __init__(self, text, username, timestamp):
        self.content = text
        self.username = username
        if(timestamp[10] == 'T'):
            timestamp = timestamp.replace("T", " ")
        self.timestamp = timestamp


class Relation():
    pass
