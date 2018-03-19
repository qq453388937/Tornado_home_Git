# -*- coding:utf-8 -*-

import logging
import constants
from .BaseHandler import BaseHandler
from utils.captcha.captcha import captcha
from utils.response_code import RET
import random
from libs.yuntongxun.SendTemplateSMS import CCP
import re


class ImageCodeHandler(BaseHandler):

    def get(self):
        code_id = self.get_argument('cur')
        pre_code_id = self.get_argument('pre')
        name, text, image = captcha.generate_captcha()  # 自己起的名字,文本,生成图片的二进制
        try:
            if pre_code_id:
                self.redis.delete('image_code_%s' % pre_code_id)  # 删除上一次的
            # redis 存储验证码的code 和验证码的文本值
            self.redis.setex('image_code_%s' % code_id, constants.PIC_CODE_EXPIRES_SECONDS, text)
        except Exception as e:
            logging.error(e)
            self.write('')
        else:
            self.set_header('Content-Type', 'image/jpg')
            self.write(image)  # 可以接受二进制


class SMSCodeHandler(BaseHandler):
    def post(self):
        if self.json_args:
            mobile = self.json_args.get("mobile")
            image_code_id = self.json_args.get("piccode_id")
            image_code_text = self.json_args.get("piccode")
            if not all([mobile, image_code_id, image_code_text]):
                # dict={
                #     'errno':RET.PARAMERR,
                #     'errmsg':'参数不完整'
                # }
                # 传入dict即可
                return self.write(dict(errno=RET.PARAMERR, errmsg='参数不完整'))
            if not re.match(r"1\d{10}", mobile):
                return self.write(dict(errno=RET.PARAMERR, errmsg="手机号错误"))
            try:
                real_image_code_text = self.redis.get('image_code_%s' % image_code_id)
            except Exception as e:
                logging.error(e)
                return self.write(dict(errno=RET.DBERR, errmsg='查询redis出错了'))
            if not real_image_code_text:
                return self.write(dict(errno=RET.NODATA, errmsg='验证码已过期'))
            if image_code_text.lower() != real_image_code_text.lower():
                return self.write(dict(errno=RET.DATAERR, errmsg='验证码输入比较错误'))
            # 生成随机验证码
            sms_code = '%04d' % random.randint(0, 9999)
            try:
                # 将验证码存储到redis
                self.redis.setex('sms_code_%s' % mobile, sms_code, constants.SMS_CODE_EXPIRES_SECONDS)
            except Exception as e:
                logging.error(e)
                return self.write(dict(errno=RET.DBERR, errmsg='插入验证码到redis出错'))

            # 发送短信
            try:
                ccp = CCP.instance()
                b = ccp.sendTemplateSMS(mobile, [sms_code, constants.SMS_CODE_EXPIRES_SECONDS / 60], 1)
                if not b:
                    return self.write(dict(errno=RET.THIRDERR, errmsg="发送验证码失败"))
            except Exception as e:
                logging.error(e)
                return self.write(dict(errno=RET.THIRDERR, errmsg="发送验证码失败"))
            self.write(dict(errno=RET.OK, errmsg='ok'))
        else:
            self.write(dict(errno=RET.OK, errmsg='json_args空!'))

    def get(self):
        """测试"""
        my_dict = {
            'errno': RET.PARAMERR,
            'errmsg': '参数不完整'
        }
        # return self.write(dict(errno=RET.PARAMERR, errmsg='参数不完整!'))
        # return self.write(my_dict)
        return self.write(dict(**my_dict))  # 写入字典会自动转换为application/json的响应头
        # 只有flask可以这样做!!!!!
        # return self.write(errno=RET.PARAMERR, errmsg="参数不完整")
