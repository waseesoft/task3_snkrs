import scrapy
from task3_snkrs.items import Task3SnkrsItem


class SnkrsSpider(scrapy.Spider):
    name = 'snkrs'

    def start_requests(self):
        url = 'https://www.snkrs.com/'
        yield scrapy.Request(url, self.parse_categories)

    def parse_categories(self, response):
        for a in response.css('ul.idparent-63 li a'):
            yield response.follow(a, self.product_pagination)

    def product_pagination(self, response):
        for a in response.css('a.product_img_link'):
            yield response.follow(a, self.parse_product)

        for a in response.css('li.pagination_next a'):
            yield response.follow(a, self.product_pagination)

    def parse_product(self, response):
        prod = Task3SnkrsItem()
        prod['product_id'] = response.css('.product_id::text').get()
        prod['name'] =  response.css('.name::text').get()
        prod['brand'] = response.css('.brand::text').get()
        prod['availability'] = response.css('.availability::text').get()
        prod['currency'] = response.css('.price_currency_code::text').get()
        prod['description'] = response.css('#short_description_content p::text').getall()
        prod['old_prices'] = response.css('.list_price::text').getall()
        prod['new_price'] = response.css('.price::attr(content)').get()
        prod['image_urls'] = response.css('.image_url::text,.alternate_image_url::text').getall()
        sizes = response.css('.units_container::text').getall()
        if all(s.isspace() for s in sizes):
            prod['sizes'] = response.css('.size_EU::text').getall()
        else:
            prod['sizes'] = sizes

        if len(prod['sizes']) == 0:
            prod['sizes'] = ['size one']
        prod['sizes'] = [s.strip() for s in prod['sizes']]

        sku = {}
        for size in prod['sizes']:
            sku[size] = {
                'size': size,
                'old_price': prod['old_prices'],
                'new_price': prod['new_price']
            }
        prod['skus'] = sku
        print(prod)





