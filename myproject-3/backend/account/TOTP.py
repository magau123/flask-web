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


def save_info(email):
    db.execute('''CREATE TABLE IF NOT EXISTS USERS(
                     ID        integer PRIMARY KEY autoincrement,
                     EMAIL     TEXT     NOT NULL,
                     KEY       CHAR(50) NOT NULL,
                     UNIQUE(EMAIL));''')
    key = pyotp.random_base32()
    db.execute('''INSERT OR IGNORE INTO USERS(EMAIL, KEY) VALUES(?, ?)''', [email, key])
    if db.execute('''SELECT KEY FROM USERS WHERE EMAIL=?;''', [email]):
        return True
    else:
        return False


def get_qrcode(email):
    save_info(email)
    select_key = db.execute('''SELECT KEY FROM USERS WHERE EMAIL=?;''', [email])[0]
    key = select_key['KEY']
    url = pyotp.totp.TOTP(key).provisioning_uri(email, issuer_name="瀛联MFA安全码")
    print(url)
    img = qrcode.make(url)
    path = '../../images/'
    for i in os.listdir(path):
        path_file = os.path.join(path,i)
        print(path_file)
        if os.path.isdir(path):
            os.remove(path_file)
        else:
            pass
    img.save(path+"/验证码.jpg".format(rand()))
    return path


def check_otp(email, code):
    select_key = db.execute('''SELECT KEY FROM USERS WHERE EMAIL=?;''', [email])[0]
    key = select_key['KEY']
    totp = pyotp.TOTP(key)
    # user_input = input("请输入验证码：")
    if code:
        res = totp.verify(code)
        print(res)
        if res:
           return True
        else:
            return False
def login():
    email = 'admin'
    get_qrcode(email)

def check():
    email = 'admin'
    code = input("请输入验证码：")
    checkout = check_otp(email, code)
    return  checkout


if __name__ == '__main__':
    # email = input("请输入邮箱：")
    login()
    check()

    # print(get_qrcode(email))
