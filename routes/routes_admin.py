from models.user import User
from routes import (
    redirect,
    current_user,
    login_required)
from utils import log
from template import render_response, response_with_headers


def admin_required(nxt_func):
    """
    一个自定义的装饰器，用于判断当前用户是否是admin，如果不是则重定向至/login
    如果是admin，则交给nxt_func继续处理
    """
    def f(request):
        u = current_user(request)
        log('admin', u)
        if u.is_admin():
            return nxt_func(request)
        else:
            return redirect('/login')
    return f


@login_required
@admin_required
def index(request):
    """
    admin 首页的路由函数
    """
    # 查找所有的用户
    all_user = User.all()
    # 课6作业6
    return render_response("admin_index.html", users=all_user)


# 课5作业7
@login_required
@admin_required
def update(request):
    """
    用于admin更新用户密码
    """
    # 解析表单的内容
    form = request.form()
    u_id = int(form['id'])
    u_password = form['password']

    # 根据u_id找出需要修改的用户对象, 并修改其密码
    u = User.find_by(id=u_id)
    # 检查对象是否存在
    if u is not None:
        u.password = u_password
        u.save()

    # 重定向回admin页面
    return redirect('/admin/users')


# 课7作业5
@login_required
@admin_required
def edit_view(request):
    return render_response("admin_password_edit.html")


# 课7作业5
@login_required
@admin_required
def update_password_salt(request):
    form = request.form()
    User.update(form)
    return redirect('/admin/users')


def route_dict():
    """
    路由字典
    key 是路由(路由就是 path)
    value 是路由处理函数(就是响应)
    """
    d = {
        '/admin/users': index,
        # 课5作业7
        '/admin/users/update': update,
        # 课7作业5
        '/admin/users/edit_view': edit_view,
        '/admin/users/update_password_salt': update_password_salt,
    }
    return d
