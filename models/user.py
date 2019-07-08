from models import Model
from models.user_role import UserRole

import hashlib


class User(Model):
    """
    User 是一个保存用户数据的 model
    现在只有两个属性 username 和 password
    """

    def __init__(self, form):
        super().__init__(form)
        self.username = form.get('username', '')
        self.password = form.get('password', '')
        self.role = form.get('role', UserRole.normal)
        # self.role = form.get('role', 'normal')

    @staticmethod
    def guest():
        form = dict(
            role=UserRole.guest,
            # role='guest',
            username='【游客】',
            id=-1,
        )
        u = User(form)
        return u

    def is_guest(self):
        # return self.username == '【游客】'
        # return self.role == 'guest'
        return self.role == UserRole.guest

    # 课5作业6:
    def is_admin(self):
        return self.role == UserRole.admin

    @classmethod
    def login_user(cls, form):
        # for 循环版本
        # us = User.all()
        # for u in us:
        #     if u.username == self.username and u.password == self.password:
        #         return True
        # return False
        # find_by 版本
        u = User.find_by(username=form['username'], password=form['password'])
        return u
        # return u is not None and u.password == self.password
        # u = User.find_by(username=self.username)
        # 不应该用下面的隐式转换
        # return u and u.password == self.password

    def validate_register(self):
        return len(self.username) > 2 and len(self.password) > 2

    @staticmethod
    def salted_password(password, salt='$!@><?>HUI&DWQa`'):
        """$!@><?>HUI&DWQa`"""
        salted = password + salt
        hash = hashlib.sha256(salted.encode()).hexdigest()
        return hash

    # 课7作业5
    @classmethod
    def update(cls, form):
        """
        用于admin更新用户密码, 并且带盐
        """
        # 解析表单的内容
        u_id = int(form['id'])
        u_password = form['password']

        # 根据u_id找出需要修改的用户对象, 并修改其密码
        u = User.find_by(id=u_id)
        # 检查对象是否存在
        if u is not None:
            u.password = cls.salted_password(u_password)
            u.save()
