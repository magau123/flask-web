    #!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
Created by liaoyangyang1 on 2018/8/22 上午9:40.
"""
from flask import Blueprint,request,render_template,jsonify,flash  #第二课增加内容
from flask import redirect,url_for,current_app,abort,session,Flask
from backend.models.UserModel import User
from backend.models import db
from flask_login import login_user,login_required,logout_user #第三课增加内容
from backend.account.TOTP import check_otp,get_qrcode,save_info,EasySqlite
from flask import session
#账户的蓝图  访问http://host:port/account 这个链接的子链接，都会跳到这里
account = Blueprint('account', __name__)  #第二课增加内容

# 访问http://host:port/account/register 这个链接，就会跳到这里
@account.route('/register',methods=(["GET","POST"]))  #第二课增加内容
#上面的链接，绑定的就是这个方法，我们给浏览器或者接口请求 一个json格式的返回
def register():  #第二课增加内容
    if request.method == 'POST':
        try:
            form = request.form
            user = User(username=form['username'], email=form['email'], password=form['password'])
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
        #return render_template('/account/checkout.html', user=user)
        if user is not None and user.password_hash is not None and user.verify_password(form['password']):  #检查密码是否正确
                login_user(user,True)  #登录操作
                flash('Please enter six digit security code.', 'success')
                return redirect( url_for(request.args.get('next') or 'account.checkout'))
        else:
            flash('Invalid email or password.', 'error')

    return render_template('/account/login.html')



@account.route('/checkout',methods=(["GET","POST"]))
def checkout(): #第三课内容
    username = session.get('username')
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
            return redirect(url_for(request.args.get('next') or 'account.complete'))
        else:
            flash('Invalid the security code.', 'error')

    return render_template('/account/checkout.html',user=username,path=path)

@account.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('admin.index'))

@account.route('/user',methods=(["GET","POST"]))  #第二课增加内容
def complete():

    return  render_template('/account/user.html')