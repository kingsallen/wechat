# coding=utf-8

from handler.base import BaseHandler

class Home(BaseHandler):
    """
    个人中心首页, 渲染个人中心页面.
    """
    def get(self):
        self.render("weixin/sysuser/personalcenter.html")


class Logout(BaseHandler):
    def get(self):
        """
        登出操作，登出后跳转到职位列表页.
        """
        pass


class ConfigHome(BaseHandler):
    """
    用户配置.
    """
    def get(self):
        """
        获取用户的配置数据并展示.
        """
        pass


class ConfigPasswd(BaseHandler):
    """
    用户密码.
    * 设置密码视图
    * 更改密码视图
    """
    def get(self):
        view = self.get_argument('view', None)
        if not view in ['set', 'change']:
            # Invalid access.
            # redirect to config home page.
            self.redirect("None")

    def post(self):
        """
        更改密码处理器
        """
        pass

    def view_set(self):
        """
        设置密码视图
        """
        pass

    def view_change(self):
        """
        更改密码视图
        """
        pass


class ConfigName(BaseHandler):
    """
    用户姓名.
    """
    def get(self):
        """
        更改姓名视图.
        """
        pass

    def post(self):
        """
        更改姓名处理器.
        """
        pass


class ConfigEmail(BaseHandler):
    """
    用户邮箱.
    """
    def get(self):
        """
        更改邮箱视图.
        """
        pass

    def post(self):
        """
        更改邮箱处理器.
        """
        pass


class ApplicationRecord(BaseHandler):
    """
    用户的申请信息.
    """
    def get(self):
        """
        我的申请信息视图.
        """
        pass


class Avatar(BaseHandler):
    """
    用户头像.
    """
    def post(self):
        """
        更新用户头像处理器.
        更新用户头像到七牛云.
        """
        pass


class FavoritePosition(BaseHandler):
    """
    感兴趣的职位.
    """
    def get(self):
        """
        感兴趣的职位视图.
        """
        pass


class Binding(BaseHandler):
    """
    用户绑定.
    """
    def get(self):
        """
        用户绑定视图.
        """
        pass

    def post(self):
        """
        用户绑定处理器.
        """
        pass


class Intension(BaseHandler):
    """
    我的兴趣.
    """
    def get(self):
        """
        我的兴趣视图.
        """
        pass

    def post(self):
        """
        我的兴趣处理器.
        """
        pass

