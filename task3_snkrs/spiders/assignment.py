import re
import datetime
from random import randint

from scrapy import Request
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from w3lib.url import add_or_replace_parameter

from task3_snkrs.items import TestItem


class AssignmentSpider(CrawlSpider):
    name = "assignment"
    PAGE_SIZE = 72
    PRICE_RE = r'[\d,.]+'

    allowed_domains = [
        'orsay.com',
    ]
    start_urls = [
        'https://www.orsay.com/de-de/produkte/',
    ]
    listings_css = [
        '.navigation-link',
    ]

    rules = [
        Rule(LinkExtractor(restrict_css=listings_css), callback='parse_pagination'),
    ]

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36'
    }

    def parse_pagination(self, response):
        yield from super().parse(response)

        urls_s = response.css('a.thumb-link')
        yield from [response.follow(url_s, callback=self.parse_product, headers=self.headers) for url_s in urls_s]
        product_count = response.css('.load-more-progress::attr(data-max)').getall()

        if product_count and int(product_count[0]) > self.PAGE_SIZE:
            product_count = int(product_count[0])
            pages = product_count // self.PAGE_SIZE + 2
            return [Request(add_or_replace_parameter(response.url, 'sz', page * self.PAGE_SIZE),
                            callback=self.parse_pagination) for page in range(2, pages)]

    def parse_product(self, response):
        item = TestItem()
        item['category'] = self.get_category(response)
        item['arrival_date'] = self.get_arrival_date()
        item['title'] = self.get_name(response)
        item['material_info'] = self.get_description(response)
        item['rating'] = randint(0, 100)

        skus = self.get_skus(response)
        for k, values in skus.items():
            item['product_id'] = f'{self.get_product_id(response)}_{k}'
            item.update(values)
            yield item

    def get_product_id(self, response):
        return response.css('.product-tile::attr(data-itemid)').getall()[0]

    def get_category(self, response):
        return re.findall('product_category_name":"(.*)\",', response.text)[0]

    def get_arrival_date(self):
        return str(datetime.date(2018, 1, 1)+datetime.timedelta(randint(1, 365)))

    def get_name(self, response):
        return response.css('.product-name::text').getall()[0]

    def get_description(self, response):
        # css = '.js-collapsible ::text'
        # css = '.product-info-title ~p::text'
        css = '.product-info-title ~p::text, .js-collapsible ::text'
        return self.clean(response.css(css).getall())

    def get_image_urls(self, response):
        return response.css('.productthumbnail::attr(src)').getall()

    def get_skus(self, response):
        skus = {}
        color_css = '.selectable.selected .swatchanchor::attr(title)'
        color = response.css(color_css).getall()[0].split('-')[-1].strip()
        sizes = self.clean(response.css('.swatches.size a::text').getall())

        for size in sizes or ['size-one']:
            sku = self.get_prices(response)
            sku['size'] = size
            sku['color'] = color
            skus[f'{color}_{size}'] = sku

        return skus

    def get_prices(self, response):
        return {
            'price': response.css('.price-sales::text').re(self.PRICE_RE)[0].replace(',', ''),
        }

    def clean(self, data):
        return [e.strip() for e in data if e and e.strip()]
