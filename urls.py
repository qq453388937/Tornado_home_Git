# -*- coding:utf-8 -*-

import os
from handlers import Passport, Verify, VerifyCode
from tornado.web import RequestHandler
# , StaticFileHandler
# 静态文件用到StaticFileHandle,这里使用继承加入了xsrf校验
from handlers.BaseHandler import MyStaticFileHandler

# 获取tornado项目的根目录的绝对路径
current_path = os.path.dirname(__file__)

handlers = [
    (r'/test', Passport.IndexHandler),
    (r'/api/piccode', Verify.ImageCodeHandler),
    (r'/api/smscode', Verify.SMSCodeHandler),
    (r'/api/register', Passport.RegisterHandler),
    (r'/api/login', Passport.LoginHandler),
    (r'/api/check_login', Passport.CheckLoginHandler),
    (r'/api/logout', Passport.CheckLoginHandler),
    (r'^/(.*)$', MyStaticFileHandler, {
        'path': os.path.join(current_path, 'html'),
        'default_filename': 'index.html'
    })
]
