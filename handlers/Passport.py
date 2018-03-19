# -*- coding:utf-8 -*-

from .BaseHandler import BaseHandler
import logging
import hashlib
import config
import re
from utils.my_session import Session

from utils.response_code import RET
# 登陆装饰其
from utils.commons import required_login


class IndexHandler(BaseHandler):
    def get(self):
        logging.warn('哈哈')
        logging.debug('debug')
        logging.info('info')
        self.write('test get')


class RegisterHandler(BaseHandler):
    def post(self):
        mobile = self.json_args.get("mobile")
        sms_code = self.json_args.get("phonecode")
        password = self.json_args.get("password")
        if not all([mobile, sms_code, password]):
            return self.write({"errno": RET.PARAMERR, "errmsg": "参数错误"})
        if not re.match(r"^1\d{10}$", mobile):
            return self.write(dict(errcode=RET.DATAERR, errmsg="手机号格式错误"))
        real_code = self.redis.get('sms_code_%s' % mobile)

        if real_code != str(sms_code):  # 加后门
            if str(sms_code) != "1111":
                return self.write({"errno": RET.DATAERR, "errmsg": "验证码无效"})
        password = hashlib.sha256(config.passwd_hash_key + password).hexdigest()
        sql = "insert into ih_user_profile(up_name, up_mobile, up_passwd) values(%(name)s, %(mobile)s, %(passwd)s);"
        try:
            # 返回主键id
            user_id = self.db.execute(sql, name=mobile, mobile=mobile, passwd=password)
        except Exception as e:
            logging.error(e)
            return self.write(dict(errno=RET.DATAEXIST, errmsg="手机号已存在"))
        # 用session记录用户登录状态
        """self就是RequestHandler对象"""
        session = Session(self)
        session.data["user_id"] = user_id
        session.data["mobile"] = mobile
        session.data["name"] = mobile
        try:
            session.save()
        except Exception as e:
            logging.error(e)
        else:
            self.write(dict(errno=RET.OK, errmsg="注册成功"))


class LoginHandler(BaseHandler):
    """登陆"""

    def post(self):
        mobile = self.json_args.get("mobile")
        password = self.json_args.get("password")
        # 校验参数
        if not all([mobile, password]):
            return self.write(dict(errno=RET.PARAMERR, errmsg="参数错误"))
        if not re.match(r"^1\d{10}$", mobile):
            return self.write(dict(errno=RET.DATAERR, errmsg="手机号错误"))
        # 检查密码是否正确
        res = self.db.get("select up_user_id,up_name,up_passwd from ih_user_profile WHERE up_mobile=%(mobile)s",
                          mobile=mobile)
        # 不管前端加不加密后端必须要加密
        password = hashlib.sha256(config.passwd_hash_key + password).hexdigest()
        if res and res["up_passwd"] == unicode(password):
            # 密码校验正确,登陆成功存储session信息
            try:
                """self就是RequestHandler对象"""
                session = Session(self)
                session.data["user_id"] = res["up_user_id"]
                session.data["mobile"] = mobile
                session.data["name"] = res['up_name']
            except Exception as e:
                logging.error(e)
            return self.write(dict(errno=RET.OK, errmsg="OK"))
        else:
            return self.write(dict(errno=RET.DATAERR, errmsg="手机号或密码错误！"))


class CheckLoginHandler(BaseHandler):
    def get(self):
        # get_current_user方法在基类中已经实现,他的返回值是session.data
        # session.data 有值返回真,没有值 返回false
        if self.get_current_user():
            # self.write(dict(errcode=RET.OK, errmsg="True", data=self.session.data.get("name")))
            self.write(
                dict(errcode=RET.OK, errmsg="True",
                     data=dict(name=self.session.data.get("name"))))  # data.data.name 看第一个点后面的
        else:
            self.write({"errcode": RET.SESSIONERR, "errmsg": "false"})


class Logout(BaseHandler):
    # 加了装饰器,在正常业务处理之外,还可能多返回一种json回去
    @required_login
    def get(self):
        """
        装饰其的理解
        inner_new_func = required_login(get)
        inner_new_func(self)
        """
        # 清除session数据
        session = Session(self)
        session.delete()
        self.write(dict(errcode=RET.OK, errmsg="退出成功"))
