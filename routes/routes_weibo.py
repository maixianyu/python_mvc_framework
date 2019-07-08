from models.comment import Comment
from models.user import User
from models.weibo import Weibo
from routes import (
    redirect,
    current_user,
    login_required,
)
from utils import log
from template import html_response


def index(request):
    """
    weibo 首页的路由函数
    """
    # 查看query中是否存在user_id
    # 存在，查看user_id用户的所有微博
    if 'user_id' in request.query:
        user_id = request.query['user_id']
        u = User.find_by(id=int(user_id))

    # 不存在，查看user_id用户的所有微博
    else:
        u = current_user(request)
        user_id = u.id

    weibos = Weibo.find_all(user_id=int(user_id))
    # 替换模板文件中的标记字符串
    return html_response('weibo_index.html', weibos=weibos, user=u)


def add(request):
    """
    用于增加新 weibo 的路由函数
    """
    u = current_user(request)
    form = request.form()
    Weibo.add(form, u.id)
    # 浏览器发送数据过来被处理后, 重定向到首页
    # 浏览器在请求新首页的时候, 就能看到新增的数据了
    return redirect('/weibo/index')


def delete(request):
    weibo_id = int(request.query['id'])
    Weibo.delete(weibo_id)
    # 注意删除所有微博对应评论
    cs = Comment.find_all(weibo_id=weibo_id)
    for c in cs:
        c.delete()
    return redirect('/weibo/index')


def edit(request):
    weibo_id = int(request.query['id'])
    w = Weibo.find_by(id=weibo_id)
    return html_response('weibo_edit.html', weibo=w)


def update(request):
    """
    用于增加新 weibo 的路由函数
    """
    form = request.form()
    Weibo.update(form)
    # 浏览器发送数据过来被处理后, 重定向到首页
    # 浏览器在请求新首页的时候, 就能看到新增的数据了
    return redirect('/weibo/index')


def comment_add(request):
    u = current_user(request)
    form = request.form()
    weibo_id = int(form['weibo_id'])

    c = Comment(form)
    c.user_id = u.id
    c.weibo_id = weibo_id
    c.save()

    log('comment add', c, u, form)
    return redirect('/weibo/index')


def weibo_owner_required(route_function):
    """
    这个函数看起来非常绕，所以你不懂也没关系
    就直接拿来复制粘贴就好了
    """

    def f(request):
        log('weibo_owner_required')
        u = current_user(request)
        if 'id' in request.query:
            weibo_id = request.query['id']
        else:
            weibo_id = request.form()['id']
        w = Weibo.find_by(id=int(weibo_id))

        if w.user_id == u.id:
            return route_function(request)
        else:
            return redirect('/weibo/index')

    return f


def comment_owner_required(route_function):
    """
    评论拥有者权限
    """
    def f(request):
        # log('weibo_owner_required')
        # 获取评论id
        form = request.form()
        if 'cid' in request.query:
            c_id = request.query['cid']
        elif 'cid' in form:
            c_id = form['cid']
        else:
            return redirect('/weibo/index')

        # 比对user id
        c = Comment.find_by(id=int(c_id))
        u = current_user(request)
        if c.user_id == u.id:
            return route_function(request)
        else:
            return redirect('/weibo/index')

    return f


# 课7作业6
def weibo_owner_or_comment_owner_required(route_function):
    """
    只有微博拥有者或者评论拥有者才给予权限
    """
    def f(request):
        # 从请求中获取comment和weibo的id
        form = request.form()
        if 'wid' in request.query and 'cid' in request.query:
            w_id = request.query['wid']
            c_id = request.query['cid']
        elif 'wid' in form and 'cid' in form:
            w_id = form['wid']
            c_id = form['cid']
        else:
            return redirect('/weibo/index')

        # 根据id找到对应的weibo和comment
        w = Weibo.find_by(id=int(w_id))
        c = Weibo.find_by(id=int(c_id))

        # 比较当前用户的id是否和comment或weibo的user id一致
        # 如果一致，说明当前用户有权限
        u = current_user(request)
        if w.user_id == u.id or c.user_id == u.id:
            return route_function(request)
        else:
            return redirect('/weibo/index')

    return f


# 课7作业6
@login_required
@weibo_owner_or_comment_owner_required
def comment_delete(request):
    # 获取comment id
    form = request.form()
    if 'cid' in request.query:
        c_id = request.query['cid']
    elif 'cid' in form:
        c_id = form['cid']
    else:
        return redirect('/weibo/index')

    # 根据comment id删除评论
    Comment.delete(int(c_id))
    return redirect('/weibo/index')


@login_required
@comment_owner_required
def comment_edit(request):
    c_id = int(request.query['cid'])
    c = Comment.find_by(id=c_id)
    return html_response('comment_edit.html', comment=c)


@login_required
@comment_owner_required
def comment_update(request):
    form = request.form()
    log("comment_update", form)
    Comment.update(form)
    return redirect('/weibo/index')


def route_dict():
    """
    路由字典
    key 是路由(路由就是 path)
    value 是路由处理函数(就是响应)
    """
    d = {
        '/weibo/add': login_required(add),
        '/weibo/delete': login_required(weibo_owner_required(delete)),
        '/weibo/edit': login_required(weibo_owner_required(edit)),
        '/weibo/update': login_required(weibo_owner_required(update)),
        '/weibo/index': login_required(index),
        # 评论功能
        '/comment/add': login_required(comment_add),
        '/comment/delete': comment_delete,
        '/comment/edit': comment_edit,
        '/comment/update': comment_update,
    }
    return d
