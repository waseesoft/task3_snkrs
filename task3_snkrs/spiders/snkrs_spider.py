from task3_snkrs.items import SnkrsItem
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor


class SnkrsSpider(CrawlSpider):
    name = 'snkrs'
    allowed_domains = ['snkrs.com']
    start_urls = [
        'https://www.snkrs.com/',
    ]
    rules = [
        Rule(LinkExtractor(restrict_css=['ul.idparent-63 li', 'li.pagination_next'])),
        Rule(LinkExtractor(restrict_css='a.product_img_link'), callback='parse_product'),
    ]

    def parse_product(self, response):
        item = SnkrsItem()
        item['item_id'] = self.get_item_id(response)
        item['name'] = self.get_name(response)
        item['brand'] = self.get_brand(response)
        item['description'] = self.get_description(response)
        item['image_urls'] = self.get_images_urls(response)
        item['skus'] = self.get_sku(response)

        return item

    def get_item_id(self, response):
        return response.css('.product_id::text').getall()[0]

    def get_name(self, response):
        return response.css('.name::text').getall()[0]

    def get_brand(self, response):
        return response.css('.brand::text').getall()[0]

    def get_description(self, response):
        return response.css('#short_description_content p::text').getall()

    def get_images_urls(self, response):
        return response.css('.image_url::text,.alternate_image_url::text').getall()

    def get_prices(self, response):
        return {
            'currency': response.css('.price_currency_code::text').getall()[0],
            'old_prices': [float(price) for price in response.css('.list_price::text').getall()],
            'new_price': float(response.css('.price::attr(content)').getall()[0]),
        }

    def get_sku(self, response):
        skus = {}
        css = '.attribute_list li:not([class=" hidden"]) span.units_container::text'
        sizes = self.clean(response.css(css).getall())

        if not sizes:
            css = '.attribute_list li:not([class=" hidden"]) span.size_EU::text'
            sizes = self.clean(response.css(css).getall()) or ['size-one']

        for index, size in enumerate(sizes):
            sku = {
                'size': size,
                'pricing': self.get_prices(response),
                'availability': response.css('.availability::text').getall()[0],
            }
            skus[size] = sku

        return skus

    def clean(self, elements):
        return [e.strip() for e in elements if e and e.strip()]
