#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
Created by liaoyangyang1 on 2018/8/22 上午9:40.
"""
from flask import Blueprint,request,render_template,jsonify,flash  #第二课增加内容
from flask import redirect,url_for,abort,session #第五课新增
from backend.models.UserModel import User,Role #第五课新增
from backend.models import db
from flask_login import login_user,login_required,logout_user,current_user #第三课增加内容 #第五课新增
from functools import wraps #第五课新增
from backend.models.UserModel import Permission #第五课新增
from backend.account.TOTP import check_otp,get_qrcode,save_info,EasySqlite
from utils.layout import layout
import  os

#账户的蓝图  访问http://host:port/account 这个链接的子链接，都会跳到这里
account = Blueprint('account', __name__)  #第二课增加内容


def permission_required(permission): #第五课新增
    """Restrict a view to users with the given permission."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# 要求管理员权限
def admin_required(f): #第五课新增
    return permission_required(Permission.ADMINISTER)(f)

# 访问http://host:port/account/register 这个链接，就会跳到这里
@account.route('/register',methods=(["GET","POST"]))  #第二课增加内容
#上面的链接，绑定的就是这个方法，我们给浏览器或者接口请求 一个json格式的返回
def register():  #第二课增加内容
    if request.method == 'POST':
        try:
            form = request.form
            user = User(username=form['username'],email=form['email'],password=form['password'])
            db.session.add(user)
            db.session.commit()
            return redirect(url_for(request.args.get('next') or 'account.login'))
        except Exception as e:
            abort(403)
    return render_template('/account/register.html')

@account.route('/login',methods=(["GET","POST"]))
def login(): #第三课内容
    if request.method == "POST":
        form = request.form #获取登录表单
        user = User.query.filter_by(username=form['username']).first()  #查出用户信息
        session['username'] = user.username
        session['role_id'] = user.role_id
        if user is not None and user.password_hash is not None and user.verify_password(form['password']):  #检查密码是否正确
            login_user(user,True)  #登录操作
            flash('You are now logged in. Welcome back!', 'success')
            return redirect( url_for(request.args.get('next') or 'account.checkout'))
        else:
            flash('Invalid email or password.', 'error')
    return render_template('/account/login.html')

@account.route('/checkout',methods=(["GET","POST"]))
def checkout(): #第三课内容
    username = session.get('username')
    dir = './frontend/static/img/{}.jpg'.format(username)
    if os.path.exists(dir):
        pass
    else:
        path = get_qrcode(username)
    if request.method == "POST":
        form = request.form #获取登录表单
        form = dict(form)
        values = form.values()

        for value in values:
            code_value=value[0]
        #     print(value[0])
        # print(code_value)
        check_value = check_otp(username,code_value)
        print(check_value)
        if check_value:
            return redirect( url_for(request.args.get('next') or 'admin.index'))
        else:
            flash('Invalid the security code.', 'error')

    return render_template('/account/checkout.html',user=username,path=path)

@account.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('admin.index'))


@account.route('/users')
@login_required
def user_list(): #第五课新增
    Role.insert_roles()
    username = session.get('username')
    role = session.get('role_id')
    user_list = User.query.outerjoin(Role, User.role_id == Role.id).all()
    return layout('/account/users.html',users=user_list,id=role,user=username)


@account.route('/edituser',methods=(["GET","POST"]))
@login_required
def user_edit(): #第五课新增
    if request.method == 'POST':
        try:
            form = request.form
            use_info = User.query.filter(User.id == form['id']).first()
            use_info.email = form['email']
            use_info.role_id = form['role_id']
            db.session.commit()
            flash('修改用户信息成功！', 'success')
        except Exception as e:
            print(e)
            flash('修改用户信息失败！', 'error')
        return redirect(url_for(request.args.get('next') or 'account.user_list'))

    id = request.values.get('id')
    user_info = User.query.filter_by(id=id).first()
    return layout('/account/edituser.html', user_info=user_info)

@account.route('/deluser')
@login_required
def user_del(): #第五课新增
    try:
        id = request.values.get('id')
        user = User.query.filter(User.id == id).first()
        db.session.delete(user)
        db.session.commit()
        flash('删除用户成功！', 'success')
    except Exception as e:
        print(e)
        flash('删除用户失败！', 'error')

    return redirect(url_for(request.args.get('next') or 'account.user_list'))


