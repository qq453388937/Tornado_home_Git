# -*- coding:utf-8 -*-
"""
session = Session(request_handler)
session.sid # 已登录,未登录
session.data
RequestHandler.get_secure_cookie()
RequestHandler.set_secure_cookie()
redis
session.session_id = 'adwadawv'
session.data["user_id"] = 123
session.data["user_mobile"] = 123
session.save()
调用者需要把request对象传进来
"""
import logging
import json
import constants


class Session(object):
    """
    1.实现session机制可以利用cookie,但不是一定要用到cookie
    2.其他形式,放到header
    3.或者url参数中

    session存储位置:
    文件
    数据库
    程序空间,容器,变量(开启多进程多线程,nginx反向代理会出现问题需要设置nginx)
    ip代理分组,ip一次会话请求只访问一个服务器
    redis缓存当中 (推荐)



    """

    def __init__(self, request_handler):
        self.request_handler = request_handler
        # 从cookie中获取sessionid 每个用户有自己的cookie
        self.session_id = self.request_handler.get_secure_cookie("session_id")
        if not self.session_id:
            # 用户第一次访问,生成uuid的sessionid
            import uuid
            self.session_id = uuid.uuid4().get_hex()
            self.data = {}
        else:
            # 尝试着取sessionid 从redis
            try:
                data = self.redis.get("sess_%s" % self.session_id)
            except Exception as e:
                logging.error(e)
                self.data = {}  # 用户没有登录,判定过期
            if not data:
                self.data = {}
            else:
                self.data = json.loads(data)  # 假设存储的是对象,json字符串

    def save(self):
        json_data = json.dumps(self.data)
        try:
            self.request_handler.redis.setex("sess_%s" % self.session_id,
                             constants.SESSION_EXPIRES_SECONDS, json_data)
        except Exception as e:
            logging.error(e)
            raise e
        else:
            self.request_handler.set_secure_cookie("session_id", self.session_id)

    def delete(self):
        # 删除cookie
        self.request_handler.clear_cookie("session_id")
        # 删除redis
        try:
            self.redis.delete("sess_%s" % self.session_id)
        except Exception as e:
            logging.error(e)
            raise e
