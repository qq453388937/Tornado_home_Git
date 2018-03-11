# -*- coding:utf-8 -*-

from .BaseHandler import BaseHandler
import logging


class IndexHandler(BaseHandler):
    def get(self):
        logging.warn('哈哈')
        logging.debug('debug')
        logging.info('info')
        self.write('test get')
