# -*- coding:utf-8 -*-

from tornado.web import RequestHandler
import json
from utils.session import Session
import tornado.web


class BaseHandler(RequestHandler):
    """基类"""

    @property
    def db(self):
        return self.application.db  # 只要继承自RequestHandler就能调到application

    @property
    def redis(self):
        return self.application.redis  # 只要继承自RequestHandler就能调到application

    def set_default_headers(self):
        self.set_header("Content-Type", 'application/json; charset=UTF-8')

    def initialize(self):
        pass

    def prepare(self):
        # self.xsrf_token  # html带上xsrf_token
        print(self.request.body.decode())
        if self.request.headers.get('Content-Type'):
            if self.request.headers.get('Content-Type').startswith('application/json'):
                self.json_args = json.loads(self.request.body.decode())
            else:
                self.json_args = None

    def write_error(self, status_code, **kwargs):
        pass

    def on_finish(self):
        pass

    def get_current_user(self):
        self.session = Session(self)
        return self.session.data


class MyStaticFileHandler(tornado.web.StaticFileHandler):
    def __init__(self, *args, **kwargs):
        """
        只要请求静态文件就触发一下xsrf植入cookie
        前端匹配 document.cookie.match("\\b_xsrf=([^;]*)\\b");
                """
        super(MyStaticFileHandler, self).__init__(*args, **kwargs)
        self.xsrf_token
        self.set_secure_cookie("itcast", "oa")
