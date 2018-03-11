# -*- coding:utf-8 -*-

import os
from handlers import Passport, Verify, VerifyCode
from tornado.web import RequestHandler, StaticFileHandler  # 静态文件用到StaticFileHandler

# 获取tornado项目的根目录的绝对路径
current_path = os.path.dirname(__file__)

handlers = [
    (r'/test', Passport.IndexHandler),
    (r'/api/piccode', Verify.ImageCodeHandler),
    (r'^/(.*)$', StaticFileHandler, {
        'path': os.path.join(current_path, 'html'),
        'default_filename': 'index.html'
    })
]
