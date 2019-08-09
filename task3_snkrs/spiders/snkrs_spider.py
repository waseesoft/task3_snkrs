import scrapy
from task3_snkrs.items import SnkrsItem


class SnkrsSpider(scrapy.Spider):
    name = 'snkrs'
    start_urls = [
        'https://www.snkrs.com/'
    ]

    def parse(self, response):
        urls_s = response.css('ul.idparent-63 li a')

        return [response.follow(url_s, callback=self.parse_pages) for url_s in urls_s]

    def parse_pages(self, response):
        yield from self.parse_product_urls(response)
        urls_s = response.css('li.pagination_next a')
        yield from [response.follow(url_s, callback=self.parse_pages) for url_s in urls_s]

    def parse_product_urls(self, response):
        urls_s = response.css('a.product_img_link')

        return [response.follow(url_s, callback=self.parse_product) for url_s in urls_s]

    def parse_product(self, response):
        item = SnkrsItem()
        item['item_id'] = self.get_item_id(response)
        item['name'] = self.get_name(response)
        item['brand'] = self.get_brand(response)
        item['availability'] = self.get_availability(response)
        item['currency'] = self.get_currency(response)
        item['description'] = self.get_description(response)
        item['image_urls'] = self.get_images_urls(response)
        item['skus'] = self.get_skus(response)

        return item

    def get_item_id(self, response):
        return response.css('.product_id::text').get()

    def get_name(self, response):
        return response.css('.name::text').get()

    def get_brand(self, response):
        return response.css('.brand::text').get()

    def get_availability(self, response):
        return response.css('.availability::text').get()

    def get_currency(self, response):
        return response.css('.price_currency_code::text').get()

    def get_description(self, response):
        return response.css('#short_description_content p::text').getall()

    def get_old_prices(self, response):
        return response.css('.list_price::text').getall()

    def get_new_price(self, response):
        return float(response.css('.price::attr(content)').get())

    def get_images_urls(self, response):
        return response.css('.image_url::text,.alternate_image_url::text').getall()

    def get_skus(self, response):
        skus = {}
        for raw_sku in self.get_filtered_sizes(response):
            skus[raw_sku] = {
                'size': raw_sku,
                'old_prices': [float(price) for price in self.get_old_prices(response)],
                'new_price': self.get_new_price(response)
            }

        return skus

    def get_filtered_sizes(self, response):
        sizes = response.css('.attribute_list li:not([class=" hidden"]) span.units_container::text').getall()
        sizes = self.filter_elements(sizes)
        if not sizes:
            sizes = response.css('.attribute_list li:not([class=" hidden"]) span.size_EU::text').getall()
            sizes = self.filter_elements(sizes)
            if not sizes:
                sizes = ['size one']

        return sizes

    def filter_elements(self, elements):
        return [e.strip() for e in elements if e != ' ' and e != '']
