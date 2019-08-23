from re import sub
from scrapy import Spider, Request
from w3lib.url import add_or_replace_parameter
from task3_snkrs.items import Item


class OrsaySpider(Spider):
    name = "orsay"
    page_size = 72
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
        if products_found > self.page_size:
            pages = products_found // self.page_size + 2
            return [Request(add_or_replace_parameter(response.url, 'sz', page * self.page_size),
                            callback=self.parse_products_url) for page in range(2, pages)]

    def parse_product(self, response):
        item = Item()
        item['id'] = self.get_product_id(response)
        item['name'] = self.get_name(response)
        item['description'] = self.get_description(response)
        item['skus'] = self.get_skus(response)
        item['image_urls'] = self.get_image_urls(response)
        item['meta'] = {'color_requests': self.color_requests(item, response)}

        return item['meta']['color_requests'].pop() if item['meta']['color_requests'] else item

    def parse_color(self, response):
        item = response.meta['item']
        item['skus'].update(self.get_skus(response))
        item['image_urls'] += self.get_image_urls(response)

        return item['meta']['color_requests'].pop() if item['meta']['color_requests'] else item

    def color_requests(self, item, response):
        query = 'ul[class="swatches color"] li[class="selectable"] a::attr(href)'
        color_urls = response.css(query).getall()
        return [Request(url, callback=self.parse_color, dont_filter=True, meta={'item': item})
                for url in color_urls]

    def get_product_id(self, response):
        return response.css('div.product-tile::attr(data-itemid)').getall()[0]

    def get_name(self, response):
        return response.css('.product-name::text').getall()[0]

    def get_image_urls(self, response):
        return response.css('img.productthumbnail::attr(src)').getall()

    def get_description(self, response):
        care = response.css('.product-material .product-info-title ~p::text').getall()
        details = response.css('.with-gutter::text').getall()
        return self.filter_empty_elements(details + care)

    def get_sizes(self, response):
        available = 'li.selectable a.swatchanchor::text'
        un_available = 'li.unselectable a.swatchanchor::text'
        return {**self.extract_sizes(response, available, True),
                **self.extract_sizes(response, un_available, False)} or {'size-one': True}

    def extract_sizes(self, response, query, is_available=None):
        return {e: is_available for e in self.filter_empty_elements(response.css(query).getall())}

    def get_prices(self, response):
        prices = {
            'currency': response.css('.current .country-currency::text').getall()[0],
            'price': sub(r',', '.', response.css('.price-sales::text').re('[\d,.]+')[0]),
            'old_prices': [sub(r',', '.', e) for e in response.css('.price-standard::text').re('[\d,.]+')],
        }
        return prices

    def filter_empty_elements(self, data):
        return [e.strip() for e in data if e.strip() != '' and e]

    def get_skus(self, response):
        sku = {}
        color_query = 'li[class="selectable selected"] .swatchanchor::attr(title)'
        color = response.css(color_query).getall()[0].split('-')[-1].strip()
        for size_key, availability in self.get_sizes(response).items():
            sku['{}_{}'.format(color, size_key)] = {
                'size': size_key,
                'color': color,
                'availability': availability,
                'prices': self.get_prices(response)
            }

        return sku
