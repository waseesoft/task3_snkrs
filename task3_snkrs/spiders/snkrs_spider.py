import scrapy
from task3_snkrs.items import SnkrsItem


class SnkrsSpider(scrapy.Spider):
    name = 'snkrs'
    response = None
    start_urls = [
        'https://www.snkrs.com/'
    ]

    def parse(self, response):
        urls_s = response.css('ul.idparent-63 li a')
        return [response.follow(url_s, callback=self.parse_pages) for url_s in urls_s]

    def parse_pages(self, response):
        yield from self.parse_product_urls(response)

        yield from [response.follow(url_s, callback=self.parse_pages) for url_s in response.css('li.pagination_next a')]

    def parse_product(self, response):
        self.response = response
        item = SnkrsItem()
        item['item_id'] = self.get_item_id()
        item['name'] = self.get_name()
        item['brand'] = self.get_brand()
        item['availability'] = self.get_availability()
        item['currency'] = self.get_currency()
        item['description'] = self.get_description()
        item['image_urls'] = self.get_images_urls()
        item['skus'] = self.get_skus()

        return item

    def parse_product_urls(self, response):
        urls_s = response.css('a.product_img_link')
        return [response.follow(url_s, callback=self.parse_product) for url_s in urls_s]

    def get_item_id(self):
        return self.response.css('.product_id::text').get()

    def get_name(self):
        return self.response.css('.name::text').get()

    def get_brand(self):
        return self.response.css('.brand::text').get()

    def get_availability(self):
        return self.response.css('.availability::text').get()

    def get_currency(self):
        return self.response.css('.price_currency_code::text').get()

    def get_description(self):
        return self.response.css('#short_description_content p::text').getall()

    def get_old_prices(self):
        return self.response.css('.list_price::text').getall()

    def get_new_price(self):
        return self.response.css('.price::attr(content)').get()

    def get_images_urls(self):
        return self.response.css('.image_url::text,.alternate_image_url::text').getall()

    def get_sizes(self):
        sizes = self.response.css('.units_container::text').getall()
        if all(s.isspace() for s in sizes):
            self.sizes = self.response.css('.size_EU::text').getall()

        if len(sizes) == 0:
            self.sizes = ['size one']
        sizes = [s.strip() for s in sizes]

        return sizes

    def get_skus(self):
        skus = {}
        for size in self.get_sizes():
            skus[size] = {
                'size': size,
                'old_price': self.get_old_prices(),
                'new_price': self.get_new_price()
            }

        return skus
