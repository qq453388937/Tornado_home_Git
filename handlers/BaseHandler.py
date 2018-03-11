# -*- coding:utf-8 -*-

from tornado.web import RequestHandler


class BaseHandler(RequestHandler):
    """基类"""

    @property
    def db(self):
        return self.application.db  # 只要继承自RequestHandler就能调到application

    @property
    def redis(self):
        return self.application.redis  # 只要继承自RequestHandler就能调到application

    def set_default_headers(self):
        pass

    def initialize(self):
        pass

    def prepare(self):
        pass

    def write_error(self, status_code, **kwargs):
        pass

    def on_finish(self):
        pass
