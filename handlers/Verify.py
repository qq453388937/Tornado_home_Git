# -*- coding:utf-8 -*-

import logging
import constants
from .BaseHandler import BaseHandler
from utils.captcha.captcha import captcha


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
        pass
