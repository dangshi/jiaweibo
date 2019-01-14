# -*- coding:utf-8 -*-

from flask import Flask
from flask import redirect, url_for, render_template, flash
from flask_login import LoginManager, login_required, login_user, logout_user, current_user

from Models import User, Post
from Models import users, get_user, posts, get_user_by_name
from Forms import LoginForm, RegisterForm, PostForm

from gstore.queryDB import gstore_user_login, gstore_user_register, gstore_user_weibo, gstore_add_follow, \
    gstore_remove_follow, gstore_post_weibo, gstore_hit_weibo
import datetime

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
    response = gstore_hit_weibo(0,10)
    if response["status"] != "OK":
        print("Failed for get hit weibo")
    stream = list()
    for item in response["result"]:
        post = Post(item["content"], item["username"], item["post_time"])
        stream.append(post)
    return render_template("stream.html", stream=stream)



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
    # 这里需要创建用户并且加入数据库中
    form = RegisterForm()
    username = form.username.data
    password = form.password.data
    repassword = form.repassword.data
    if password != repassword:
        print("密码不一致")
        flash("Your password doesn't match!", "error")
        pass
    elif username and password and repassword:
        respon = gstore_user_register(username, password)
        if respon["status"] == "OK":
            return redirect(url_for('index'))
        else:
            print("注册失败")
            flash("Register failed!", "error")
            return render_template('register.html', form=form)
    return render_template('register.html', form=form)


@app.route('/login', methods=('GET', 'POST'))
def login():
    """
    login()
    用户通过验证后，通过login_user()函数来登入
    """
    form = LoginForm()
    username = form.username.data
    password = form.password.data
    if username and password:
        respon = gstore_user_login(username, password)
        if respon["status"] == "OK":
            print(respon)
            userid = respon["result"]["userid"]
            User.create_user(userid,username, password)
            user = get_user(userid)
            login_user(user)
            return redirect(url_for('stream', username=username))
        else:
            flash("Login failed!", "error")
    return render_template('login.html', form=form)


# 需要登入才能访问的路由用login_required装饰器修饰

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You've been logged out! Come back soon!", "success")
    return redirect(url_for('index'))


@app.route('/stream', methods=['GET', 'POST'])
@app.route('/stream/<username>', methods=['GET', 'POST'])
def stream(username = None):
    """
    获得stream
    如果是username不为none并且username不是current user相同，则返回username对应用户的微博列表
    如果username不为none并且就是current user，则返回用户的首页（所关注人的微博）
    如果username为none，返回任何用户的最新n条微博
    """
    stream = []
    template = 'stream.html'
    user = None
    if username:
        # 是当前用户，使用user_stream的页面展示当前用户的微博
        user = get_user_by_name(username)
        if username == current_user.get_username():
            template = 'user_stream.html'
        # username 对应的weibo
        response = gstore_user_weibo(username, offset=0, size=10)
        if response["status"] != "OK":
            print("fail for get weibo of username:", username)
        stream = list()
        for item in response["result"]:
            post = Post(item["content"], item["username"], item["post_time"])
            stream.append(post)
        return render_template(template, stream=stream, user=user)

    else:
        stream = posts[:10] # 热门微博简单地就取posts中前十条
        return render_template(template, stream=stream, user=user)


@app.route('/post',  methods=['GET', 'POST'])
@login_required
def post():
    """
    发布一条新的微博
    :return:
    """
    now = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    form = PostForm()
    if form.content.data:
        response = gstore_post_weibo(current_user.get_username(),form.content.data, now)

        if(response["status"] == "OK"):
            flash('Your Message has been posted!', 'Success')
            return redirect(url_for('stream/'+current_user.get_username()))
        else:
            flash("Post failed", 'error')

    return render_template('post.html', form = form)


@app.route('/follow/<username>')
@login_required
def follow(username):
    """
    关注某个用户
    :param username: 想关注的用户名
    :return: 被关注用户的stream
    """
    response = gstore_add_follow(current_user.username, username)
    if(response["status"] == "OK"):
        flash("关注用户: "+str(username), "Success")
    else:
        flash("关注失败",  "error")
    return redirect(url_for('stream', username=username))


@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    """
    取关某个用户
    :param username: 取关用户的用户名
    :return: 当前用户的首页
    """
    response = gstore_remove_follow(current_user.username, username)
    if (response["status"] == "OK"):
        flash("取消关注用户: " + str(username), "Success")
    else:
        flash("取消关注操作失败", "error")
    return redirect(url_for('stream', username=username))


if __name__ == '__main__':
    app.run(debug=True)



