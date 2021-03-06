#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
Created by liaoyangyang1 on 2018/8/22 下午1:50.
"""
from flask_login import UserMixin,AnonymousUserMixin  #第二课增加内容
from werkzeug.security import check_password_hash, generate_password_hash  #第二课增加内容
from backend.models import db  #第二课增加内容
from backend.views import login_manager #第三课新增
import pymysql

class User(UserMixin, db.Model):  #第二课增加内容
    __tablename__ = 'users'  #这是我们将来建出来的表的表名，在这里定义，下面的都是字段名和字段类型长度这些
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    #脱敏
    @property
    def password(self):  #第二课增加内容
        raise AttributeError('`password` is not a readable attribute')
    #加密
    @password.setter
    def password(self, password):  #第二课增加内容
        self.password_hash = generate_password_hash(password)
    #校验密码
    def verify_password(self, password):  #第二课增加内容
        return check_password_hash(self.password_hash, password)

    def __repr__(self):  #第二课增加内容
        return '<User \'%s\'>' % self.username
# class mysql:
#     def __init__(self): #初始化
#         self.db = pymysql.connect(
#             host="127.0.0.1",
#             user ="root",
#             password ="123456",
#             database ="web",
#             charset ="utf8")
#         sql = '''CREATE TABLE IF NOT EXISTS USERS(
#                              ID        integer PRIMARY KEY ,
#                              USERNAME     CHAR (50)    NOT NULL,
#                              code       CHAR(50) NOT NULL,
#                              UNIQUE(USERNAME));'''
#         self.cursor = self.db.cursor()
#         self.cursor.execute(sql)
#         self.db.commit()
#
#     # 执行modify(修改)相关操作
#     def execute_modify_mysql(self, sql, parm=None):  # 实现一个插入,修改
#         self.cursor.execute(sql, parm)
#         data = self.cursor.fetchall()
#         self.db.commit()
#         return data
#
#     def execute_select_query(self, sql):  # 查询语句
#         self.cursor.execute(sql)
#         self.db.commit()
#
#
#
#     # def __del__(self):  # 结束
#     #     self.cursor.close()
#     #     self.db.close()


class AnonymousUser(AnonymousUserMixin): #第三课新增
    def can(self, _):
        return False

    def is_admin(self):
        return False


login_manager.anonymous_user = AnonymousUser   #第三课新增


@login_manager.user_loader
def load_user(user_id): #第三课新增
    return User.query.get(int(user_id))