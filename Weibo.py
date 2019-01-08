# -*- coding:utf-8 -*-

from flask import Flask
from flask import redirect, url_for, render_template, flash
from flask_login import LoginManager, login_required, login_user, logout_user

from Models import User
from Models import users, get_user    # 用list实现，未使用gstore
from Forms import LoginForm

app = Flask(__name__)

# flask-wtf框架处理表单时止CSRF攻击的机制
# 不加会出现KeyError: 'A secret key is required to use CSRF
app.config.from_pyfile('CONFIG')

login_manager = LoginManager()
login_manager.session_protection = 'strong'
# 未登入访问了一个login_required的view，flask-login会重定向到 log in view
login_manager.login_view = 'login'
login_manager.init_app(app)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/index')
def index():
    return 'welcome back to index page !'


@login_manager.user_loader
def load_user(user_id):
    """
    load_user(user_id)
    提供一个 user_loader回调。
    这个回调用于从会话中存储的用户ID重新加载用户对象
    接受用户的unicode ID作为参数并返回相应的用户对象
    如果失败会返回None
    """
    try:
        return get_user(user_id)
    except:
        return None


@app.route('/register', methods=('GET', 'POST'))
def register():
    # TODO
    # 这里需要创建一个用户并且加入数据库中
    User.create_user(username='test user 1', password='123456')
    return 'create user !'


@app.route('/login', methods=('GET', 'POST'))
def login():
    """
    login()
    用户通过验证后，通过login_user()函数来登入
    """
    form = LoginForm()
    if form.validate_on_submit():
        print('form validate! username:%s' % form.username.data)
        try:
            for user in users:
                if user.get_username() == form.username.data:
                    login_user(user)
                    return redirect(url_for('index'))
        except:
            print('some exception')
    return render_template('login.html', form=form)


# 需要登入才能访问的路由用login_required装饰器修饰

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You've been logged out! Come back soon!", "success")
    return redirect(url_for('index'))


@app.route('/stream')
@app.route('/stream/<username>')
def stream(username = None):
    """
    获得stream
    如果是username不为none并且username不是current user相同，则返回username对应用户的微博列表
    如果username不为none并且就是current user，则返回用户的首页（所关注人的微博）
    如果username为none，返回任何用户的最新n条微博 
    """
    return('a stream web page')


@app.route('/post')
@login_required
def post():
    """
    发布一条新的微博
    :return: 
    """
    return('page to publish post')


@app.route('/follow/<username>')
@login_required
def follow(username):
    """
    关注某个用户
    :param username: 想关注的用户名
    :return: 被关注用户的stream
    """
    pass


@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    """
    取关某个用户
    :param username: 取关用户的用户名
    :return: 当前用户的首页
    """
    pass





if __name__ == '__main__':
    app.run(debug=True)
