# -*- coding:utf-8 -*-

from flask import Flask
from flask import redirect, url_for, render_template, flash
from flask_login import LoginManager, login_required, login_user, logout_user, current_user

from Models import User, Post
from Models import get_user
from Forms import LoginForm, RegisterForm, PostForm
from flask import request

from gstore.queryDB import gstore_user_login, gstore_user_register, gstore_user_weibo, gstore_add_follow, \
    gstore_remove_follow, gstore_post_weibo, gstore_hit_weibo, gstore_user_info, gstore_user_following_weibo, \
    gstore_user_detail_info, gstore_get_username
import datetime
import math

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
@app.route('/index',methods=['GET', 'POST'])
def index():
    page = request.args.get('p', '1')
    if not page:
        page = 1
    limit = request.args.get('limit', '10')
    if not limit:
        limit = 10
    limit = int(limit)
    page = int(page)
    offset = (page - 1) * limit
    response = gstore_hit_weibo(offset,limit)
    if response["status"] != "OK":
        print("Failed for get hit weibo")
    stream = list()
    for item in response["result"]:
        post = Post(item["content"], item["username"], item["post_time"])
        stream.append(post)

    total = 100
    return render_template("index.html", stream=stream, total=total, limit=limit, current_page=page, url="index")



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
        username = gstore_get_username(user_id)
        response = gstore_user_detail_info(username)
        # user = User(userid, username, password)
        if (response["status"] != "OK"):
            print("error occur in getting user info, username:", username)
            flash("User don't exist", "error")
            return
        result = response["result"]
        user = User(user_id=user_id,  username=username, post_num=result["posts_num"],
                    following_num=result["following_num"], followed_num=result["followed_num"],
                   following=result["following"], followed=result["followed"])
        return user
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
            return redirect(url_for('login'))
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
            userid = respon["result"]["userid"]
            response = gstore_user_info(username)
            # user = User(userid, username, password)
            if (response["status"] != "OK"):
                print("error occur in getting user info, username:", username)
                flash("User don't exist", "error")
                return
            result = response["result"]
            user = User(user_id=userid, password=password, username=username, post_num=result["posts_num"],
                        following_num=result["following_num"], followed_num=result["followed_num"])
            if login_user(user):
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
    page = request.args.get('p', '1')
    if not page:
        page = 1
    limit = request.args.get('limit', '10')
    if not limit:
        limit = 10
    limit = int(limit)
    page = int(page)
    offset = (page - 1) * limit

    stream = []
    template = 'stream.html'
    user = None
    if current_user:
        username = current_user.get_username()
        response = gstore_user_info(username)
        if (response["status"] != "OK"):
            print("error occur in getting user info, username:", username)
            flash("User don't exist", "error")
            return
        result = response["result"]
        user = User(user_id=result["userid"],username=username, post_num=result["posts_num"], following_num=result["following_num"],
                    followed_num=result["followed_num"])

        response = gstore_user_following_weibo(username, offset=offset, size=limit)
        if response["status"] != "OK":
            print("fail for get weibo of username:", username)
        stream = list()
        for item in response["result"]:
            post = Post(item["content"], item["username"], item["post_time"])
            stream.append(post)

        if len(stream) < limit:
            total = page
        else:
            total = page + 1
        return render_template(template, stream=stream, user=user, total=total, limit=limit, current_page=page, url="stream", username=username)

    else:
        return url_for("index")

@app.route('/user_stream/<username>', methods=['GET', 'POST'])
def user_stream(username=None):
    page = request.args.get('p', '1')
    if not page:
        page = 1
    limit = request.args.get('limit', '10')
    if not limit:
        limit = 10
    limit = int(limit)
    page = int(page)
    offset = (page - 1) * limit

    template = 'user_stream.html'
    stream = []
    user = None
    if username:
        response = gstore_user_info(username)
        if(response["status"] != "OK"):
            print("error occur in getting user info, username:", username)
            flash("User don't exist", "error")
            return
        result = response["result"]
        user = User(user_id=result["userid"],username=username, post_num=result["posts_num"], following_num=result["following_num"],
                    followed_num=result["followed_num"])

        # username 对应的weibo
        response = gstore_user_weibo(username, offset=offset, size=limit)
        if response["status"] != "OK":
            print("fail for get weibo of username:", username)
        for item in response["result"]:
            post = Post(item["content"], item["username"], item["post_time"])
            stream.append(post)
        if len(stream) < limit:
            total = page
        else:
            total = page + 1
        return render_template(template, stream=stream, user=user, total=total, limit=limit, current_page=page,
                               url="user_stream", username=username)
    else:
        return url_for("index")




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
            return redirect(url_for('user_stream',username=current_user.get_username()))
        else:
            flash("Post failed", 'error')

    return render_template('post.html', form = form)


@app.route('/follow/<username>',  methods=['GET', 'POST'])
@login_required
def follow(username):
    """
    关注某个用户
    :param username: 想关注的用户名
    :return: 被关注用户的stream
    """
    response = gstore_add_follow(current_user.get_username(), username)
    if(response["status"] == "OK"):
        flash("关注用户: "+str(username), "Success")
        return redirect(url_for('user_stream', username=username))
    else:
        flash("关注失败",  "error")
        return redirect(url_for('user_stream', username=username))


@app.route('/unfollow/<username>', methods=['GET', 'POST'])
@login_required
def unfollow(username):
    """
    取关某个用户
    :param username: 取关用户的用户名
    :return: 当前用户的首页
    """
    response = gstore_remove_follow(current_user.get_username(), username)
    if (response["status"] == "OK"):
        flash("取消关注用户: " + str(username), "Success")
    else:
        flash("取消关注操作失败", "error")
    return redirect(url_for('user_stream', username=username))



@app.route('/user_following/<username>', methods=['GET', 'POST'])
@login_required
def show_following(username):
    page = request.args.get('p', '1')
    if not page:
        page = 1
    limit = request.args.get('limit', '10')
    if not limit:
        limit = 10
    limit = int(limit)
    page = int(page)
    offset = (page - 1) * limit

    template = "follow_list.html"
    response = gstore_user_detail_info(username)
    if(response["status"] != "OK"):
        flash("Failed for searching user:", username)
    following = response["result"]["following"]
    following_users = list()
    for name in following[offset:offset+limit]:
        resp = gstore_user_info(name)
        if(resp["status"] == "OK"):
            result = resp["result"]
            user = User(result["userid"],name, post_num=result["posts_num"],
                        following_num=result["following_num"], followed_num=result["followed_num"])
            following_users.append(user)
    total = math.ceil(len(following) / limit)
    return render_template(template, users=following_users, url='show_following', username=username,
                           total=total, limit=limit, current_page=page)


@app.route('/user_followed/<username>', methods=['GET', 'POST'])
@login_required
def show_followed(username):
    page = request.args.get('p', '1')
    if not page:
        page = 1
    limit = request.args.get('limit', '10')
    if not limit:
        limit = 10
    limit = int(limit)
    page = int(page)
    offset = (page - 1) * limit

    template = "follow_list.html"
    response = gstore_user_detail_info(username)
    if (response["status"] != "OK"):
        flash("Failed for searching user:", username)
    followed = response["result"]["followed"]
    followed_users = list()
    for name in followed[offset:offset+limit]:
        resp = gstore_user_info(name)
        if (resp["status"] == "OK"):
            result = resp["result"]
            user = User(result["userid"],name, post_num=result["posts_num"],
                        following_num=result["following_num"], followed_num=result["followed_num"])
            followed_users.append(user)

    total = math.ceil(len(followed) / limit)
    return render_template(template, users=followed_users,url='show_followed', username=username,
                           total=total, limit=limit, current_page=page)

# 分页展示页面
@app.route('/pages', methods=['GET','POST'])
def pages():
    page = request.args.get('p', '1')
    if not page:
        page = 1
    limit = request.args.get('limit', '10')
    if not limit:
        limit = 10
    limit = int(limit)
    page = int(page)
    offset = (page - 1) * limit
    print('search gstore with offset %d and limit %d' % (offset, limit))

    # search database
    response = gstore_hit_weibo(offset, limit)
    if response["status"] != "OK":
        print("Failed for get hit weibo")
    stream = list()
    for item in response["result"]:
        post = Post(item["content"], item["username"], item["post_time"])
        stream.append(post)


     # total是全部微博数
    total = 100
    return render_template("stream.html", stream=stream, total=total, limit=limit, current_page=page)

if __name__ == '__main__':
    app.run(debug=True)



