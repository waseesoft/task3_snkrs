from scrapy import Request
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from w3lib.url import add_or_replace_parameter

# from task3_snkrs.task3_snkrs.items import OrsayItem


class OrsaySpider(CrawlSpider):
    name = "orsay"
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

    def parse_pagination(self, response):
        yield from super().parse(response)

        urls_s = response.css('a.thumb-link')
        yield from [response.follow(url_s, callback=self.parse_product) for url_s in urls_s]
        product_count = response.css('.load-more-progress::attr(data-max)').getall()

        if product_count and int(product_count[0]) > self.PAGE_SIZE:
            product_count = int(product_count[0])
            pages = product_count // self.PAGE_SIZE + 2
            return [Request(add_or_replace_parameter(response.url, 'sz', page * self.PAGE_SIZE),
                            callback=self.parse_pagination) for page in range(2, pages)]

    def parse_product(self, response):
        item = dict()
        item['product_id'] = self.get_product_id(response)
        item['name'] = self.get_name(response)
        item['description'] = self.get_description(response)
        item['image_urls'] = self.get_image_urls(response)
        item['skus'] = self.get_skus(response)
        item['meta'] = {'requests': self.get_color_requests(item, response)}

        return self.request_or_item(item)

    def parse_color(self, response):
        item = response.meta['item']
        item['skus'].update(self.get_skus(response))
        item['image_urls'] += self.get_image_urls(response)
        return self.request_or_item(item)

    def get_color_requests(self, item, response):
        urls = response.css('.swatches.color li[class="selectable"] a::attr(href)').getall()
        return [Request(url, callback=self.parse_color, dont_filter=True, meta={'item': item})
                for url in urls if url]

    def request_or_item(self, item):
        if item.get('meta') and item['meta'].get('requests'):
            return item['meta']['requests'].pop()
        else:
            del item['meta']
            return item

    def get_product_id(self, response):
        return response.css('.product-tile::attr(data-itemid)').getall()[0]

    def get_name(self, response):
        return response.css('.product-name::text').getall()[0]

    def get_description(self, response):
        css = '.product-info-title ~p::text, .js-collapsible ::text'
        return self.clean(response.css(css).getall())

    def get_image_urls(self, response):
        return response.css('.productthumbnail::attr(src)').getall()

    def get_skus(self, response):
        skus = {}
        color_css = '.selectable.selected .swatchanchor::attr(title)'
        color = response.css(color_css).getall()[0].split('-')[-1].strip()
        sizes = self.clean(response.css('.swatches.size a::text').getall())
        oos_sizes = self.clean(response.css('.unselectable a.swatchanchor::text').getall())

        for size in sizes or ['size-one']:
            sku = self.get_prices(response)
            sku['availability'] = size in oos_sizes
            sku['size'] = size
            sku['color'] = color
            skus[f'{color}_{size}'] = sku

        return skus

    def get_prices(self, response):
        return {
            'currency': response.css('.current .country-currency::text').getall()[0],
            'price': response.css('.price-sales::text').re(self.PRICE_RE)[0].replace(',', ''),
            'old_prices': [e.replace(',', '') for e in response.css('.price-standard::text')
                .re(self.PRICE_RE)],
        }

    def clean(self, data):
        return [e.strip() for e in data if e and e.strip()]
