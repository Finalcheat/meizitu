#!/usr/bin/env python
# -*- coding: utf-8 -*-

import scrapy
import re
import datetime
from meizitu.items import MeizituItem


class MeizituSpider(scrapy.Spider):
    '''
    妹子图spider
    '''

    name = 'meizitu'
    allowed_domains = ['meizitu.com']
    start_urls = [
        'http://www.meizitu.com/a/',
    ]

    def parse(self, response):
        items = response.xpath('//li[@class="wp-item"]/div/div[@class="pic"]/a/@href').extract()
        for r in items:
            yield scrapy.Request(r, callback = self.parse_item)

        last = response.xpath('//div[@id="wp_page_numbers"]/ul/li[last()]/a/@href').extract()
        if last:
            next_page = response.xpath('//div[@id="wp_page_numbers"]/ul/li[last()-1]/a/@href').extract()
            if next_page:
                next_page_url = '{}{}'.format(self.start_urls[0], next_page[0])
                yield scrapy.Request(next_page_url, callback = self.parse)


    def parse_item(self, response):
        item = MeizituItem()

        title = response.xpath('//div[@class="metaRight"]/h2/a')
        item['title'] = title.xpath('text()').extract()[0]
        item['href'] = title.xpath('@href').extract()[0]

        tags = response.xpath('//div[@class="metaRight"]/p/text()').extract()
        tags = tags[0] if tags else ''
        r = re.findall('Tags:(.*),', tags)
        tags = r[0].split(',') if r else []
        _tags = []
        for r in tags:
            s = r.strip()
            if s:
                _tags.append(r.strip())
        item['tags'] = _tags

        day = response.xpath('//div[@class="metaLeft"]/div[@class="day"]/text()').extract()
        day = int(day[0]) if day else 1
        month_year = response.xpath('//div[@class="metaLeft"]/div[@class="month_Year"]/text()').extract()
        month_year = month_year[0] if month_year else ''
        month_year_list = re.findall(".*?(\d+).*?(\d+)", month_year)
        month_year_list = month_year_list[0] if month_year_list else ''
        month = int(month_year_list[0]) if month_year_list else 1
        year = int(month_year_list[1]) if month_year_list else 2016
        date = datetime.date(year = year, month = month, day = day)
        item['day'] = date.strftime('%Y-%m-%d')

        pictures = response.xpath('//div[@id="picture"]/p/img')
        _pictures = []
        for p in pictures:
            src = p.xpath('@src').extract()
            if src:
                _pictures.append(src[0])
        if not _pictures:
            pictures = response.xpath('//p/img')
            _pictures = []
            for p in pictures:
                src = p.xpath('@src').extract()
                if src:
                    _pictures.append(src[0])

        item['pictures'] = _pictures

        item['update_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        yield item

