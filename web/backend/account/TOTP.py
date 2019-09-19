#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pyotp
import qrcode
import sqlite3
import random
import string
import  os


class EasySqlite:
    """
    sqlite数据库操作工具类
    database: 数据库文件地址，例如：db/mydb.db
    """
    _connection = None

    def __init__(self, database):
        # 连接数据库
        self._connection = sqlite3.connect(database, check_same_thread=False)

    def _dict_factory(self, cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def execute(self, sql, args=[], result_dict=True, commit=True) -> list:
        """
        执行数据库操作的通用方法
        Args:
        sql: sql语句
        args: sql参数
        result_dict: 操作结果是否用dict格式返回
        commit: 是否提交事务
        Returns:
        list 列表，例如：
        [{'id': 1, 'name': '张三'}, {'id': 2, 'name': '李四'}]
        """
        if result_dict:
            self._connection.row_factory = self._dict_factory
        else:
            self._connection.row_factory = None
        # 获取游标
        _cursor = self._connection.cursor()
        # 执行SQL获取结果
        _cursor.execute(sql, args)
        if commit:
            self._connection.commit()
        data = _cursor.fetchall()
        _cursor.close()
        return data


db = EasySqlite('DevOps.db')

selectWord = string.ascii_letters + "0123456789"


def rand():
    # count = 10
    # len = 20
    re = ""
    for y in range(12):
        re += random.choice(selectWord)
    return re


def save_info(username):
    db.execute('''CREATE TABLE IF NOT EXISTS USERS(
                     ID        integer PRIMARY KEY autoincrement,
                     USERNAME     TEXT     NOT NULL,
                     KEY       CHAR(50) NOT NULL,
                     UNIQUE(USERNAME));''')
    key = pyotp.random_base32()
    db.execute('''INSERT OR IGNORE INTO USERS(USERNAME, KEY) VALUES(?, ?)''', [username, key])
    if db.execute('''SELECT KEY FROM USERS WHERE USERNAME=?;''', [username]):
        return True
    else:
        return False


def get_qrcode(username):
    save_info(username)
    select_key = db.execute('''SELECT KEY FROM USERS WHERE USERNAME=?;''', [username])[0]
    key = select_key['KEY']
    url = pyotp.totp.TOTP(key).provisioning_uri(username, issuer_name="瀛联MFA安全码")
    # print(url)
    img = qrcode.make(url)
    path = '/static/img/{}.jpg'.format(rand())
    img.save('./frontend'+path)

    return path


def check_otp(username, code):
    select_key = db.execute('''SELECT KEY FROM USERS WHERE USERNAME=?;''', [username])[0]
    # print(select_key)
    #print(select_key)
    key = select_key['KEY']
    totp = pyotp.TOTP(key)
    # print(totp)
    # user_input = input("请输入验证码：")
    if code:
        res = totp.verify(code)
        if res:
           return True
        else:
            return False


if __name__ == '__main__':
    # username = input("请输入邮箱：")
    # get_qrcode(username)
    username = name()
    print(username)
    code = input("请输入验证码：")
    print(check_otp(username,code))
    # print(get_qrcode(username))
