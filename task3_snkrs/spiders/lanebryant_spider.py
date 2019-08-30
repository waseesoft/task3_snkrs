import json
import re

from scrapy import Request
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from task3_snkrs.items import LanebryantItem


class LanebryantSpider(CrawlSpider):
    name = "lanebryant"
    image_req_t = 'https:{url}_ms?req=set,json'
    image_url_t = 'https://lanebryant.scene7.com/is/image/{url}'

    allowed_domains = [
        'lanebryant.com',
        'lanebryant.scene7.com',
    ]
    start_urls = [
        'https://www.lanebryant.com',
    ]
    listings_css = [
        '.mar-subnav-links-column',
        '.mar-pagination a',
    ]
    products_css = [
        '.mar-prd-item-image-container'
    ]

    rules = [
        Rule(LinkExtractor(restrict_css=listings_css)),
        Rule(LinkExtractor(restrict_css=products_css), callback='parse_product'),
    ]

    def parse_product(self, response):
        raw_product = self.get_raw_product(response)

        item = LanebryantItem()
        item['product_id'] = self.get_product_id(raw_product)
        item['name'] = self.get_name(raw_product)
        item['brand'] = self.get_brand()
        item['description'] = self.get_description(response)
        item['image_urls'] = []
        item['skus'] = self.get_skus(raw_product)
        item['url'] = response.url
        item['meta'] = {'requests': self.image_requests(raw_product)}

        return self.request_or_item(item)

    def parse_image_urls(self, response):
        item = response.meta['item']
        item['image_urls'] += self.get_image_urls(response)
        return self.request_or_item(item)

    def get_raw_product(self, response):
        raw = json.loads(response.css('#pdpInitialData::text').getall()[0])
        return raw['pdpDetail']['product'][0]

    def get_product_id(self, raw_product):
        return self.clean(raw_product['product_id'])

    def get_name(self, raw_product):
        return self.clean(raw_product['product_name'])[0]

    def get_brand(self):
        return 'Lane Bryant'

    def get_description(self, response):
        return self.clean(response.css('#tab1 ::text').getall())

    def get_image_urls(self, response):
        raw_urls = json.loads(re.search(r'({.*})', response.text).group())
        raw_urls = raw_urls['set']['item']

        return [self.image_url_t.format(url=raw['i']['n']) for raw in raw_urls] \
            if isinstance(raw_urls, list) else [self.image_url_t.format(url=raw_urls['i']['n'])]

    def get_skus(self, data):
        skus = {}

        colors = data['all_available_colors'][0]['values']
        sizes = data['all_available_sizes']

        color_map = {c.get('id'): c.get('name') for c in colors}
        size_map = {size.get('id'): size.get('value') for size in sizes[0]['values']}

        for raw_sku in data['skus']:
            sku = self.pricing(raw_sku['prices'])
            sku['color'] = color_map.get(raw_sku['color'])
            sku['availability'] = True
            sku['size'] = size_map.get(raw_sku['size'], '') + raw_sku.get('cupSize', '') \
                          + raw_sku.get('bandSize', '')

            skus[raw_sku['sku_id']] = sku

        return skus

    def image_requests(self, raw_product):
        return [Request(self.image_req_t.format(url=color['sku_image']),
                        callback=self.parse_image_urls) for color in
                raw_product['all_available_colors'][0]['values']]

    def request_or_item(self, item):
        if item.get('meta') and item['meta'].get('requests'):
            request = item['meta']['requests'].pop()
            request.meta['item'] = item
            return request
        else:
            del item['meta']
            return item

    def pricing(self, prices):
        currencies = {'$': 'USD'}
        currency = re.search(r'\W', prices['sale_price']).group()
        return {
            **{k: v.replace(currency, '') for k, v in prices.items()},
            'currency': currencies[currency]
        }

    def clean(self, data):
        if isinstance(data, list):
            return [e.strip() for e in data if e and e.strip()]
        elif isinstance(data, str):
            return data.strip()
