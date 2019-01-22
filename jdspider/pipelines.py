# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import os
import re
import json
from datetime import datetime


class JDspiderPipeline(object):
    def process_item(self, item, spider):
        return item

class JsonPipeline(object):

    def open_spider(self, spider):
        filename = './../%s.json'%spider.name
        self.fp = open(filename, 'a', encoding='utf-8')

    def process_item(self, item, spider):
        obj = dict(item)
        string = json.dumps(obj, ensure_ascii=False)
        self.fp.write(string + '\n')
        return item

    def close_spider(self, spider):
        self.fp.close()
