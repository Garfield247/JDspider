# -*- coding: utf-8 -*-
import re
import json
import scrapy
from jdspider.items import PhonespiderItem

class JdSpider(scrapy.Spider):
    name = 'jd'
    # allowed_domains = ['www.jd.com']
    start_urls = ['https://list.jd.com/list.html?cat=9987,653,655']

    def parse(self, response):
        for phone in list(set(re.findall(r'href="//(item.jd.com/\d+.html)"',response.text))):
            print(phone)
            yield scrapy.Request(url = 'https://%s'%phone,callback=self.parse_info)
        next_utl = response.urljoin(response.xpath('.//a[contains(text(),"下一页")]/@href').extract_first()) if response.xpath('.//a[contains(text(),"下一页")]/@href').extract_first() else None
        if next_utl:
            yield scrapy.Request(url=next_utl,callback=self.parse)

    def parse_info(self, response):
        item = PhonespiderItem()
        item['phone_brand'] = response.xpath('.//div[starts-with(@class,"J-crumb-br")]/div[@class="inner border"]/div[@class="head"]/a/text()').extract_first()
        item['phone_name'] = response.xpath('.//div[@class="item ellipsis"]/text()') .extract_first()
        # item['reference_price'] = response.xpath('').extract_first()
        item['parameter'] = [dict(zip(dl.xpath('.//dt/text()').extract(),[i for i in dl.xpath('.//dd/text()').extract() if '\n' not in i])) for dl in response.xpath('.//div[@class="Ptable"]//dl')]
        phone_id = re.findall(r'item.jd.com/(\d+).html',response.url)[0]
        comment_url = 'https://sclub.jd.com/comment/productPageComments.action?&productId={pid}&score=0&sortType=5&page=0&pageSize=10&isShadowSku=0&rid=0&fold=1'.format(pid=phone_id)
        yield scrapy.Request(url=comment_url,callback=self.parse_comment,meta={'item':item,'phone_id':phone_id})

    def parse_comment(self, response):
        cmts = json.loads(response.text).get('comments')
        if len(cmts)>0:
            for cmt in cmts:
                item = response.meta['item']
                comments = {}
                comments['comment_user'] = cmt.get('nickname')
                comments['appraise'] = cmt.get('content')
                comments['\+'] = cmt.get('productColor')
                comments['buy_size'] = cmt.get('productSize')
                comments['buy_date'] = cmt.get('creationTime')
                comments['buy_client'] = cmt.get('userClientShow')
                comments['score'] = cmt.get('score')
                comments['upvote'] = cmt.get('usefulVoteCount')
                item['comments'] = comments
                yield item
            phone_id = response.meta['phone_id']
            page_num = int(re.findall(r'page=(\d+)', response.url)[0])+1
            comment_url = 'https://sclub.jd.com/comment/productPageComments.action?&productId={pid}&score=0&sortType=5&page={pagenum}&pageSize=10&isShadowSku=0&rid=0&fold=1'.format(pid=phone_id,pagenum=page_num)
            yield scrapy.Request(url=comment_url,callback=self.parse_comment,meta={'item':response.meta['item'],'phone_id':phone_id})
