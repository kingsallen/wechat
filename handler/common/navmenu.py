# -*- coding: utf-8 -*-

from tornado.web import UIModule

class NavMenuModule(UIModule):
    """老微信样式的 menu"""

    def render(self):
        return self.render_string('refer/common/navmenu.html')
