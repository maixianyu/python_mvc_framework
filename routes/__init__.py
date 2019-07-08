from utils import log
from models.message import Message
from models.user import User
from models.session import Session
from template import template, response_with_headers, render_response

import random


def random_string():
    """
    生成一个随机的字符串
    """
    seed = 'sdfsdafasfsdfsdwtfgjdfghfg'
    s = ''
    for i in range(16):
        # 这里 len(seed) - 2 是因为我懒得去翻文档来确定边界了
        random_index = random.randint(0, len(seed) - 2)
        s += seed[random_index]
    return s


def current_user(request):
    if 'session_id' in request.cookies:
        session_id = request.cookies['session_id']
        s = Session.find_by(session_id=session_id)
        if s is None or s.expired():
            return User.guest()
        else:
            user_id = s.user_id
            u = User.find_by(id=user_id)
            if u is None:
                return User.guest()
            else:
                return u
    else:
        return User.guest()


def error(request):
    """
    根据 code 返回不同的错误响应
    目前只有 404
    """
    return b'HTTP/1.x 404 NOT FOUND\r\n\r\n<h1>NOT FOUND</h1>'


def redirect(url):
    """
    浏览器在收到 302 响应的时候
    会自动在 HTTP header 里面找 Location 字段并获取一个 url
    然后自动请求新的 url
    """
    headers = {
        'Location': url,
    }
    # 增加 Location 字段并生成 HTTP 响应返回
    # 注意, 没有 HTTP body 部分
    # HTTP 1.1 302 ok
    # Location: /todo
    #
    r = response_with_headers(headers, 302) + '\r\n'
    return r.encode()


def login_required(route_function):
    """
    response = login_required(route_edit)
    response(request)
    这个函数看起来非常绕
    所以暂时不懂也没关系
    就直接复制粘贴拿来用就好了
    """
    def f(request):
        u = current_user(request)
        if u.is_guest():
            return redirect('/login')
        else:
            return route_function(request)
    return f


def route_index(request):
    """
    主页的处理函数, 返回主页的响应
    """
    header = 'HTTP/1.x 210 VERY OK\r\nContent-Type: text/html\r\n'
    body = template('index.html')
    u = current_user(request)
    body = body.replace('{{username}}', u.username)
    r = header + '\r\n' + body
    return r.encode()


def route_login(request):
    """
    登录页面的路由函数
    """
    headers = {
        'Content-Type': 'text/html',
    }
    log('login, headers', request.headers)
    log('login, cookies', request.cookies)
    user_current = current_user(request)
    log('current user', user_current)
    if request.method == 'POST':
        form = request.form()
        user_login = User.login_user(form)
        if user_login is not None:
            # 下面是把用户名存入 cookie 中
            # headers['Set-Cookie'] = 'user={}'.format(u.username)
            # session 会话
            # 设置一个随机字符串来当令牌使用
            session_id = random_string()
            form = dict(
                session_id=session_id,
                user_id=user_login.id,
            )
            s = Session.new(form)
            s.save()
            headers['Set-Cookie'] = 'session_id={}'.format(session_id)
            result = '登录成功'
        else:
            result = '用户名或者密码错误'
    else:
        result = ''

    body = template('login.html')
    body = body.replace('{{result}}', result)
    body = body.replace('{{username}}', user_current.username)
    # 1. response header
    # 2. headers
    # 3. body
    header = response_with_headers(headers)
    r = '{}\r\n{}'.format(header, body)
    log('login 的响应', r)
    return r.encode()


def route_register(request):
    if request.method == 'POST':
        form = request.form()
        u = User.new(form)
        if u.validate_register():
            u.save()
            result = '注册成功<br> <pre>{}</pre>'.format(User.all())
        else:
            result = '用户名或者密码长度必须大于2'
    else:
        result = ''
    body = template('register.html')
    body = body.replace('{{result}}', result)
    header = 'HTTP/1.1 210 VERY OK\r\nContent-Type: text/html\r\n'
    r = header + '\r\n' + body
    return r.encode()


@login_required
def message_view(request):
    ms = Message.all()
    return render_response("messages.html", messages=ms)


def save_message_and_redirect(data):
    """
    保存新的message，并返回重定向响应
    """
    if len(data) > 0:
        m = Message.new(data)
        m.save()
    return redirect("/message/view")


@login_required
def add_message_get(request):
    data = request.query
    return save_message_and_redirect(data)


@login_required
def add_message_post(request):
    data = request.form()
    return save_message_and_redirect(data)


# @login_required
def route_static(request):
    """
    静态资源的处理函数, 读取图片并生成响应返回
    """
    filename = request.query['file']
    path = 'static/{}'.format(filename)
    with open(path, 'rb') as f:
        header = b'HTTP/1.1 200 OK\r\nContent-Type: image/gif\r\n'
        r = header + b'\r\n' + f.read()
        return r


def route_dict():
    """
    路由字典
    key 是路由(路由就是 path)
    value 是路由处理函数(就是响应)
    """
    # f = login_required(route_message)
    # route_index(request)
    # f(request)
    d = {
        '/': route_index,
        '/static': route_static,
        '/login': route_login,
        '/register': route_register,
        '/message/view': message_view,
        '/add_message_get': add_message_get,
        '/add_message_post': add_message_post,
        # '/messages': f,
    }
    return d
