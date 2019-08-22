import scrapy
import w3lib.url
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

        products_found = int(response.css('.load-more-progress::attr(data-max)').get())
        if products_found > 72:
            pages = products_found // 72 + 1
            return [scrapy.Request(w3lib.url.add_or_replace_parameter(response.url, 'sz', page * 72),
                                   callback=self.parse_products_url) for page in range(2, pages)]

    def parse_product(self, response):
        item = Item()
        item['item_id'] = self.get_item_id(response)
        item['name'] = self.get_name(response)
        item['description'] = self.get_description(response)
        item['skus'] = self.get_skus(response)
        item['image_urls'] = self.get_image_urls(response)
        item['meta'] = self.color_requests(item, response)
        color_requests = item['meta']

        return color_requests.pop() if color_requests else item

    def parse_color(self, response):
        item = response.meta['item']
        item['skus'] += self.get_skus(response)
        item['image_urls'] += self.get_image_urls(response)
        color_requests = item['meta']

        return color_requests.pop() if color_requests else item

    def color_requests(self, item, response):
        color_urls = response.css('ul[class="swatches color"] li[class="selectable"] a::attr(href)').getall()

        return [scrapy.Request(url, callback=self.parse_color, meta={'item': item})
                for url in color_urls]

    def get_item_id(self, response):
        return response.css('div.product-tile::attr(data-itemid)').get()

    def get_name(self, response):
        return response.css('.product-name::text').get()

    def get_image_urls(self, response):
        return response.css('img.productthumbnail::attr(src)').getall()

    def get_currency(self, response):
        return response.css('.current .country-currency::text').get()

    def get_availability(self, response):
        is_available = response.css('p.in-stock-msg ::text').get()
        return True if is_available == 'Auf Lager' else False

    def get_description(self, response):
        return self.filter_empty_elements(response.css('.with-gutter::text').getall())

    def get_sizes(self, response):
        return self.filter_empty_elements(response.css('li.selectable a.swatchanchor::text').getall())

    def get_colors(self, response):
        return self.filter_colors(response.css('.swatchanchor::attr(title)').getall())

    def get_selected_color(self, response):
        return self.filter_colors(response.css('li[class="selectable selected"] .swatchanchor::attr(title)').getall())

    def get_old_prices(self, response):
        return self.remove_commas(response.css('.price-standard::text').re('[\d,.]+'))

    def get_sale_price(self, response):
        return self.remove_commas(response.css('.price-sales::text').re('[\d,.]+'))

    def remove_commas(self, elements):
        return [e.replace(',', '') for e in elements]

    def filter_empty_elements(self, data):
        return [e.strip() for e in data if e.strip() != '']

    def filter_colors(self, colors):
        return [e.split('-')[-1].strip() for e in colors if e.strip() != '']

    def get_skus(self, response):
        sku = {}
        for raw_sku in self.get_sizes(response) or ['size-one']:
            sku[raw_sku] = {
                'size': raw_sku,
                'color': self.get_selected_color(response)[0],
                'availability': self.get_availability(response),
                'currency': self.get_currency(response),
                'old_prices': self.get_old_prices(response),
                'price': self.get_sale_price(response)[0],
            }
        return [sku]
