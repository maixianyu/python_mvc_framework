from models.todo import Todo
from models.user import User
from routes import (
    redirect,
    current_user,
    login_required)
from utils import log
from template import response_with_headers, template


@login_required
def index(request):
    """
    todo 首页的路由函数
    """
    u = current_user(request)
    # todos = Todo.all()
    todos = Todo.find_all(user_id=u.id)

    # 下面这行生成一个 html 字符串
    # 课5作业4，添加了时间的显示
    todo_html = """
        <h3>
            添加时间: {}, 更新时间：{}
            <br>
            {} : {}
            <a href="/todo/edit?id={}">编辑</a>
            <a href="/todo/delete?id={}">删除</a>
        </h3>

    """

    # 课5作业4，添加了时间的显示
    import datetime

    def dt(t):
        return datetime.datetime.fromtimestamp(t).strftime('%Y-%m-%d %H:%M:%S')

    todo_html = ''.join([
        todo_html.format(
            dt(t.created_time), dt(t.updated_time), t.id, t.title, t.id, t.id
        ) for t in todos
    ])

    # 替换模板文件中的标记字符串
    body = template('todo_index.html')
    body = body.replace('{{todos}}', todo_html)

    # 下面 3 行可以改写为一条函数, 还把 headers 也放进函数中
    headers = {
        'Content-Type': 'text/html',
    }
    header = response_with_headers(headers)
    r = header + '\r\n' + body
    return r.encode()


def add(request):
    """
    用于增加新 todo 的路由函数
    """
    form = request.form()
    u = current_user(request)

    t = Todo.new(form)
    t.user_id = u.id
    t.save()
    # 浏览器发送数据过来被处理后, 重定向到首页
    # 浏览器在请求新首页的时候, 就能看到新增的数据了
    return redirect('/todo')
    # return index(request)


def delete(request):
    todo_id = int(request.query['id'])
    Todo.delete(todo_id)
    return redirect('/todo')


def match_user(next_func):
    """
    一个自定义的装饰器
    该函数用于判断当前登陆的用户不是这个todo的创建者
    如果不是，则重定位到/todo
    如果是，则继续交给next_func处理
    """
    def f(request):
        method = request.method
        # 根据query的id获取todo对象
        # 因为是与todo id匹配，所以todo id一定会通过GET或者POST放在request中
        # 比如 edit 是 GET，update 是 POST
        if method == 'GET':
            todo_id = int(request.query['id'])
        elif method == 'POST':
            todo_id = int(request.form()['id'])
        # 如果都不是，直接重定向到/todo
        else:
            return redirect('/todo')

        t = Todo.find_by(id=todo_id)
        # todo对象对应的uid
        t_uid = t.user_id

        # 获取当前用户id
        u = current_user(request)

        # 当前用户uid与todo uid不匹配
        if u.id != t_uid:
            return redirect('/todo')
        # 如果当前用户id与todo的uid一致
        else:
            return next_func(request)
    return f


@login_required
@match_user
def edit(request):
    """
    todo 首页的路由函数
    """
    # 课5作业2：由于权限判断都放在了装饰器，所以这里直接写edit逻辑
    # 替换模板文件中的标记字符串
    todo_id = int(request.query['id'])
    t = Todo.find_by(id=todo_id)
    body = template('todo_edit.html')
    body = body.replace('{{todo_id}}', str(todo_id))
    body = body.replace('{{todo_title}}', str(t.title))
    # 下面 3 行可以改写为一条函数, 还把 headers 也放进函数中
    headers = {
        'Content-Type': 'text/html',
    }
    header = response_with_headers(headers)
    r = header + '\r\n' + body
    return r.encode()


@login_required
@match_user
def update(request):
    """
    用于增加新 todo 的路由函数
    """
    # 课5作业2：由于权限判断都放在了装饰器，所以这里直接写update逻辑
    form = request.form()
    log('todo update', form, form['id'], type(form['id']))
    todo_id = int(form['id'])
    t = Todo.find_by(id=todo_id)
    t.title = form['title']

    # 课5作业3：update保存之前更新updated_time
    import time
    t.updated_time = int(time.time())
    t.save()

    # 浏览器发送数据过来被处理后, 重定向到首页
    # 浏览器在请求新首页的时候, 就能看到新增的数据了
    return redirect('/todo')


def route_dict():
    """
    路由字典
    key 是路由(路由就是 path)
    value 是路由处理函数(就是响应)
    """
    d = {
        '/todo': index,
        '/todo/add': add,
        '/todo/delete': delete,
        '/todo/edit': edit,
        '/todo/update': update,
    }
    return d
