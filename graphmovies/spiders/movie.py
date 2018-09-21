# -*- coding: utf-8 -*-
from scrapy import Request, Spider, FormRequest
import re
import json
from copy import deepcopy


class MovieSpider(Spider):
    name = 'movie'
    allowed_domains = ['www.graphmovies.com']
    start_urls = ['http://www.graphmovies.com/']
    
    home_headers = {
        'Host': 'www.graphmovies.com',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
    }
    
    home_url = 'http://www.graphmovies.com/home/2/'
    
    index_headers = {
        'Host': 'www.graphmovies.com',
        'Origin': 'http://www.graphmovies.com',
        'Referer': 'http://www.graphmovies.com/home/2/',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
    }
    
    index_url = 'http://www.graphmovies.com/home/2/get.php?orkey={orkey}'
    
    detail_headers = {
        'Host': 'www.graphmovies.com',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
    }
    
    detail_url = 'http://www.graphmovies.com/home/2/graph.php?orkey={orkey}'
    
    script_url = 'http://www.graphmovies.com/home/2/script.php?orkey={orkey}'
    
    script_headers = {
        'Host': 'www.graphmovies.com',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    data = {
        'type': 'movie',
        't': '0',
        'sort': '1',
        # 'tag': '0',
        # 'zone': '0',
        'showtime': '0',
        'level': '0',
    }
    
    def start_requests(self):
        yield Request(self.home_url, headers=self.home_headers, callback=self.parse_home)
    
    def parse_home(self, response):
        # print(response.text)
        pattern = re.compile('get.php\?orkey=(.*?)\',', re.S)
        result = re.search(pattern, response.text)
        print(result)
        if result:
            orkey = result.group(1)
            print('orkey')
            index_url = self.index_url.format(orkey=orkey)
            print(index_url)
            p = 0
            form_data = deepcopy(self.data)
            form_data['p'] = str(p)
            for tag in range(1, 62):
                for zone in range(1, 12):
                    form_data = deepcopy(form_data)
                    form_data['tag'] = str(tag)
                    form_data['zone'] = str(zone)
                    yield FormRequest(index_url, headers=self.index_headers, formdata=form_data,
                                      callback=self.parse_index,
                                      meta={'p': p, 'orkey': orkey, 'form_data': form_data})
    
    def parse_index(self, response):
        # print(response.text)
        data = json.loads(response.text)
        items = data.get('data', [])
        for item in items:
            print(item['orkey'])
            orkey = item['orkey']
            detail_url = self.detail_url.format(orkey=orkey)
            print(detail_url)
            yield Request(detail_url, headers=self.detail_headers, callback=self.parse_detail,
                          meta={'orkey': orkey, 'item': item, 'form_data': response.meta.get('form_data')})
        if data.get('status') == 1:
            p_next = response.meta.get('p') + 15
            form_data = deepcopy(response.meta.get('form_data'))
            form_data['p'] = str(p_next)
            index_url = self.index_url.format(orkey=response.meta.get('orkey'))
            yield FormRequest(index_url, headers=self.index_headers, formdata=form_data, callback=self.parse_index,
                              meta={'p': p_next, 'orkey': response.meta.get('orkey'),
                                    'form_data': response.meta.get('form_data')})
    
    def parse_detail(self, response):
        # print(response.text)
        pattern = re.compile('get.php\?orkey=(.*?)\',', re.S)
        result = re.search(pattern, response.text)
        # print(result)
        if result:
            orkey = result.group(1)
            script_headers = deepcopy(self.script_headers)
            script_headers['Referer'] = self.detail_url.format(orkey=response.meta.get('orkey'))
            print(orkey)
            script_url = self.script_url.format(orkey=orkey)
            print(script_url, script_headers)
            
            yield Request(script_url, callback=self.parse_script, headers=script_headers,
                          meta={'item': response.meta.get('item'), 'form_data': response.meta.get('form_data')})
    
    def parse_script(self, response):
        item = response.meta.get('item')
        pairs = json.loads(response.text).get('data', [])
        item['pairs'] = pairs
        item['args'] = response.meta.get('form_data')
        yield item
