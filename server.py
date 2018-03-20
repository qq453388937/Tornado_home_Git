# -*- coding:utf-8 -*-
import tornado.web
import tornado.ioloop
import tornado.options
import tornado.httpserver
import torndb
import redis

from tornado.options import define, options
from tornado.web import RequestHandler
from urls import handlers  # url抽离
import config  # 导入配置文件

# urllib.quote('http://www.idehai.com/wechat8023/profile')
define('port', type=int, default=8888, help='run port')


class MyApplication(tornado.web.Application):
    """定义基类Application"""

    def __init__(self, *args, **kwargs):
        super(MyApplication, self).__init__(*args, **kwargs)
        self.db = torndb.Connection(
            **config.torndb_settings  # 抽离到配置文件中
        )
        self.redis = redis.StrictRedis(
            **config.redis_settings  # 抽离到配置文件中
        )


def main():
    """tail -f log # 动态显示"""
    options.logging = config.log_leve  # 日志级别
    options.log_file_prefix = config.log_file  # 注意下划线,存储到日志文件
    tornado.options.parse_command_line()
    app = MyApplication(  # 调用自己的Application
        handlers, **config.settings
    )
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    # http_server.bind(8888)
    # http_server.start()
    tornado.ioloop.IOLoop.current().start()


if __name__ == '__main__':
    main()

"""
mysqldump -uroot -p123 ihome > xxx.sql
arttemplate.js
https://github.com/aui/artTemplate.js

"""
