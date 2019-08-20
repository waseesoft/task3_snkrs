import math
import scrapy
from task3_snkrs.items import Item


class OrsaySpider(scrapy.Spider):
    name = "orsay"
    start_urls = [
        'https://www.orsay.com/de-de/produkte/'
    ]

    def parse(self, response):
        urls_s = response.css('a.refinement-category-link')

        return [response.follow(url_s, callback=self.parse_categories) for url_s in urls_s]

    def parse_categories(self, response):
        urls_s = response.css('a.refinement-category-link')

        return [response.follow(url_s, callback=self.parse_products_url) for url_s in urls_s]

    def parse_products_url(self, response):
        urls_s = response.css('a.thumb-link')
        yield from [response.follow(url_s, callback=self.parse_product) for url_s in urls_s]

        products_found = int(self.get_total_products(response))
        if products_found > 72:
            pages = math.ceil(products_found / 72) + 1
            load_more = '?sz={}'
            return [response.follow(load_more.format(page * 72), callback=self.parse_products_url)
                    for page in range(2, pages)]

    def parse_product(self, response):
        item = Item()
        item['item_id'] = self.get_id(response)
        item['name'] = self.get_name(response)
        item['description'] = self.get_description(response)
        item['availability'] = self.get_availability(response)
        item['currency'] = self.get_currency(response)
        item['skus'] = [self.get_skus(response)]
        color_urls = self.get_color_wise_urls(response)

        return item if not color_urls else self.color_request(color_urls, item)

    def color_request(self, color_urls, item):
        return scrapy.Request(color_urls.pop(), callback=self.parse_sizes, meta={'item': item, 'urls': color_urls})

    def parse_sizes(self, response):
        item = response.meta['item']
        sku = item['skus']
        sku.append(self.get_skus(response))
        item['skus'] = sku
        color_urls = response.meta['urls']

        return self.color_request(color_urls, item) if color_urls else item

    def get_total_products(self, response):
        return response.css('.load-more-progress::attr(data-max)').get()

    def get_id(self, response):
        return response.css('div.product-tile::attr(data-itemid)').get()

    def get_name(self, response):
        return response.css('.product-name::text').get()

    def get_image_urls(self, response):
        return response.css('img.productthumbnail::attr(src)').getall()

    def get_currency(self, response):
        return response.css('.current .country-currency::text').get()

    def get_availability(self, response):
        return response.css('p.in-stock-msg ::text').get()

    def get_description(self, response):
        return response.css('.with-gutter::text').re(r'(\S.*)')

    def get_sizes(self, response):
        return self.filter_sizes(response.css('li.selectable a.swatchanchor::text').re('(\S.*)'))

    def get_colors(self, response):
        return response.css('.swatchanchor::attr(title)').re('-\s(.*)')

    def get_selected_color(self, response):
        return response.css('li[class="selectable selected"] .swatchanchor::attr(title)').re_first('-\s(.*)')

    def get_color_wise_urls(self, response):
        return response.css('ul[class="swatches color"] li[class="selectable"] a::attr(href)').getall()

    def get_old_prices(self, response):
        return self.remove_commas(response.css('.price-standard::text').re('[\d,.]+'))

    def get_sale_price(self, response):
        return response.css('.price-sales::text').re_first('[\d.]+')

    def remove_commas(self, elements):
        return [e.replace(',', '') for e in elements]

    def filter_sizes(self, data):
        return ['one-size'] if not data else data

    def get_skus(self, response):
        sku = {
            self.get_selected_color(response): {
                'sizes': self.filter_sizes(self.get_sizes(response)),
                'image_urls': self.get_image_urls(response),
            }
        }
        return sku
