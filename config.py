# -*- coding:utf-8 -*-
import os

# redis 配置抽离
redis_settings = dict(
    host='127.0.0.1',
    port=6379,
)
torndb_settings = dict(
    host="127.0.0.1",
    database="test1",
    user="root",
    password="123",  # 看源码得知默认3306端口
)

settings = {
    'debug': True,
    'static_path': os.path.join(os.path.dirname(__file__), 'static'),
    'template_path': os.path.join(os.path.dirname(__file__), 'template'),
    # 'static_url_prefix': "/ChinaNumber1", # 一般默认用/static ,这个参数可以修改默认的静态请求开头路径
    # 'cookie_secret': '0Q1AKOKTQHqaa+N80XhYW7KCGskOUE2snCW06UIxXgI=',  # 组合拳,安全cookie import base64,uuid
    # 'xsrf_cookies': True

}

log_file = os.path.join(os.path.dirname(__file__), 'logs/log.txt')
log_leve = 'debug'
