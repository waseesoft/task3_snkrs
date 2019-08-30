import json

from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from w3lib.url import add_or_replace_parameters

from task3_snkrs.items import LanebryantItem


class LanebryantSpider(CrawlSpider):
    name = "lanebryant"

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
    rules = [
        Rule(LinkExtractor(restrict_css=listings_css)),
        Rule(LinkExtractor(restrict_css='.mar-prd-item-image-container'), callback='parse_product'),
    ]

    def parse_product(self, response):
        data = json.loads(response.css('#pdpInitialData::text').getall()[0])
        data = data['pdpDetail']['product'][0]

        item = LanebryantItem()
        item['product_id'] = self.get_product_id(data)
        item['name'] = self.get_name(data)
        item['brand'] = self.get_brand()
        item['description'] = self.get_description(response)
        item['skus'] = self.get_skus(data)
        item['meta'] = {'requests': self.image_requests(response, data, item)}

        return self.request_or_item(item)

    def parse_image_urls(self, response):
        data = response.meta['data']
        item = response.meta['item']

        if item.get('image_urls'):
            item['image_urls'] += self.get_image_urls(response, data)
        else:
            item['image_urls'] = self.get_image_urls(response, data)

        return self.request_or_item(item)

    def image_requests(self, response, data, item):
        return [response.follow(add_or_replace_parameters(color['sku_image'] + '_ms', {'req': 'set,json'}),
                callback=self.parse_image_urls, meta={'item': item, 'data': data})
                for color in data['all_available_colors'][0]['values']]

    def request_or_item(self, item):
        if item.get('meta') and item['meta'].get('requests'):
            return item['meta']['requests'].pop()
        else:
            del item['meta']
            return item

    def get_product_id(self, data):
        return data['product_id']

    def get_name(self, data):
        return data['product_name']

    def get_brand(self):
        return 'Lane Bryant'

    def get_description(self, response):
        return [e.strip() for e in response.css('#tab1 ::text').getall() if e and e.strip()]

    def get_image_urls(self, response, data):
        raw_urls = json.loads(response.text.split('(', 1)[1].strip(');')[:-3])
        server_url = 'https:' + data['scene7_params']['server_url']
        raw_urls = raw_urls['set']['item']

        return [server_url + raw_url['i']['n'] for raw_url in raw_urls] if isinstance(raw_urls, list) \
            else [server_url + raw_urls['i']['n']]

    def pricing(self, prices):
        currencies = {'$': 'USD'}
        currency = prices['sale_price'].strip()[0]
        return {
            **{k: v.replace(currency, '') for k, v in prices.items()},
            'currency': currencies[currency]
        }

    def get_skus(self, data):
        skus = {}

        colors = data['all_available_colors'][0]['values']
        sizes = data['all_available_sizes']

        for raw_sku in data['skus']:
            sku = self.pricing(raw_sku['prices'])
            sku['color'] = self.match(colors, 'name', raw_sku['color'])
            sku['availability'] = True

            if len(sizes) > 1:
                sku['cup_size'] = raw_sku['cupSize']
                sku['band_size'] = raw_sku['bandSize']
            else:
                sku['size'] = self.match(sizes[0]['values'], 'value', raw_sku['size'])

            skus[raw_sku['sku_id']] = sku

        return skus

    def match(self, seq, key, value):
        return [e[key] for e in seq if e['id'] == value][0]
