import json

from scrapy.spiders import CrawlSpider, Rule, Request
from scrapy.linkextractors import LinkExtractor

from task3_snkrs.items import NeimanItem


class NeimanSpider(CrawlSpider):
    name = 'neimanmarcus'
    HTTPS = 'https:'

    custom_settings = {
        'USER_AGENT': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36"
    }

    allowed_domains = [
        'neimanmarcus.com',
    ]

    start_urls = [
        'https://www.neimanmarcus.com/en-cn/index.jsp',
    ]

    cookies = {
        'tms_data': '{DT-2017.03}a3HwxssoiZzaMm5Pj2Bv6OVfV52gp3oiNhZzH+Q1Et/Dqvj4UZJdUi3o2xJa8'
                    'M7HpxN6YGZIZum7DZENeq2mpKWsMMyjHzZzskVuLSi5glDPBfxqHllZ2ATy6SBwEqoLuEFuFVN'
                    'hhw9H6USiUQk2MevVCpxX43W932GrkdrWBWOZ10w0I54Cujvasl9kPL6NE/N0GxD1AkccaD6JWG'
                    'dOXiXFLSyAYhxfiwLqbrXsVfFrMH6XHHgvBstXkyq9kUG4IChvW47uZiQ+jAxwXSW/Ntm2X9NpzG'
                    'mhOp+i/CGDKbq9ExXV4hL92pOz47MfElVC5s91r6+5gB7jaH62Nnzt8A+kYcGo1PzCSEFeBvbKmXd'
                    '/UQaNS9npeuy296A5gmaaUtWQgp+J9A91MzoIpTo5PZ5CkCwIllUtuyVNcy/XxtjRjozw2k36quitU'
                    'KtOqIE3Y0di38hvqLx5Y9ZS5tqi127/sj1E0AwyB5IGnP2vpuheaKsICNkiPPIWc4FBYlN49JWVRHlm'
                    'o0ApsItKZCQgjHCozMyntDUHvtbH7bIeXeTIcxia6/Zss4sz+jgsQh8t3+ggHCty76ZxrT9Kwrb54rEX'
                    'GkSanU9W5IyiJmrYcCb84IbHXsPw/eJjp7UjP2C0uMV5NDEbxpFJYdZLkGGuHy9dZx5h3XINJorm2r8XN'
                    'iYZtbheJvfkxkpM3pXdsG9RarRp52UEcsPVsJreUHygoLJF8DI6A/P9G5bkAZUWmUdOkpejNE6nWFn/wzW'
                    'tTk6XH2F/FHK8yYGl7vu/Zdrvu3XaUnmOliCgqKZJulwli6EMjFh+oo57Qu8k3q/+NQ7lfO18FeTD8flEte'
                    '4D9CEnqWgTRKmcnqcbvrE8LHY4MRgvFWT6EVUPA/rTo2wx9+qojGkfbwWrNA+L/0ojXjIvddFI+4AoKTsKA'
                    '63gqYmoRcYrbu6OGXSrlzuVvTaxKE+qzGBxEF9Sb96krdEeD0fWUQ==',
    }

    cook = {
        'tms_data': '{DT-2017.03}a3HwxssoiZzaMm5Pj2Bv6L13Gv8Ad/WZkJm2zLBiJ22quEI2eCcOen+zdhEJJvHeeOOXi+MO99UjG2/1D+hl4AXI0xqxMcBJcNKRoDmB8W5Ptb0z0I9kIPIlYImXaHDdOdwGiYZVK7VYetLzT9+AlvcXAgQLwm8YRoSydQX9y/iR/GCfWSi0wro7/kwt7J5Bi/FFkjSxBX6XHCkgroK52hUKgW/YC1MZ5sJseydRx1IoiHRiDZy5ztxXq6ZzvseaBT8nS56U9EH3crgXmw7726TvadPC383EPCcEAJZTuPTQi1SjH0Vww5owXy0GVtVTHgQUbpz2HR2jg/liv8BYRgT2uIMscZUHtj+3+LXEgL6h5VNpAM7BXr6dpAo87UmpKZAaZhUufcW4Hj6OhLjcc5Ae8ZOY/g3Ei3DxvzB6aoaOI4FwvVc1FhRMcX3UGkXfsYvcNKgQnb6ELb7f4yJm9mSzR3oVmqDMXFPe1HnsR95VAvDwEZlbY18XLrU5bGYP4J/0xyiH9OE+PfysOstZsnMZxsPhNo1VZiWNo5S8enqzFf7dhClsTL5qAjscfQTNv1JIrXORKfF6DcBf6i/91Q8zGK1KAKTv37mIV3btzFSeNu7fPUOTtBM/TFgJzzGLe7AYYInEvPqfxx0yQ+d5xzRk7NNsgoykAQK83uIbFnVuJmCggiAv7tabslD7R/ZCKyfdbvFE1siLr8Lhn00KWEBdt9hvDuoEV1DiP+oaNg7B5sIaxERI55GR2VgK/9C0UqiFyyO95itCF45/y/ruyNakse0Ttc80Q/BXLhImKOOi5HrGsbxf+PEuy5H84QG5/6EhXwB4UpWJQc82EysqOlMBhT/Jya6TmzWB9Ztp6jH4a2Wox15pF6VYlVHKTbLEIjmMZm1x+b3GYJaY0NPLNV8jeFLpB3Tbs9RoUsHPbuN1gR29OXRa7GfW2oCg6AHm0/shfgNgeMf+9AsLDt7Mhg=='
    }

    c = '{DT-2017.03}a3HwxssoiZzaMm5Pj2Bv6L13Gv8Ad/WZkJm2zLBiJ22quEI2eCcOen+zdhEJJvHeeOOXi+MO99UjG2/1D+hl4AXI0xqxMcBJcNKRoDmB8W5Ptb0z0I9kIPIlYImXaHDdOdwGiYZVK7VYetLzT9+AlvcXAgQLwm8YRoSydQX9y/iR/GCfWSi0wro7/kwt7J5Bi/FFkjSxBX6XHCkgroK52hUKgW/YC1MZ5sJseydRx1IoiHRiDZy5ztxXq6ZzvseaBT8nS56U9EH3crgXmw7726TvadPC383EPCcEAJZTuPTQi1SjH0Vww5owXy0GVtVTHgQUbpz2HR2jg/liv8BYRgT2uIMscZUHtj+3+LXEgL6h5VNpAM7BXr6dpAo87UmpKZAaZhUufcW4Hj6OhLjcc5Ae8ZOY/g3Ei3DxvzB6aoaOI4FwvVc1FhRMcX3UGkXfsYvcNKgQnb6ELb7f4yJm9mSzR3oVmqDMXFPe1HnsR95VAvDwEZlbY18XLrU5bGYP4J/0xyiH9OE+PfysOstZsnMZxsPhNo1VZiWNo5S8enqzFf7dhClsTL5qAjscfQTNv1JIrXORKfF6DcBf6i/91Q8zGK1KAKTv37mIV3btzFSeNu7fPUOTtBM/TFgJzzGLe7AYYInEvPqfxx0yQ+d5xzRk7NNsgoykAQK83uIbFnVuJmCggiAv7tabslD7R/ZCKyfdbvFE1siLr8Lhn00KWEBdt9hvDuoEV1DiP+oaNg7B5sIaxERI55GR2VgK/9C0UqiFyyO95itCF45/y/ruyNakse0Ttc80Q/BXLhImKOOi5HrGsbxf+PEuy5H84QG5/6EhXwB4UpWJQc82EysqOlMBhT/Jya6TmzWB9Ztp6jH4a2Wox15pF6VYlVHKTbLEIjmMZm1x+b3GYJaY0NPLNV8jeFLpB3Tbs9RoUsHPbuN1gR29OXRa7GfW2oCg6AHm0/shfgNgeMf+9AsLDt7Mhg=='

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, callback=self.parse, cookies=self.cookies)

    listings_css = [
        '.arrow-button--right',
        '.menu-wrapper a',
    ]

    rules = [
        Rule(LinkExtractor(restrict_css=listings_css)),
        Rule(LinkExtractor(restrict_css='.product-thumbnail__link'), callback='parse_product',
             process_request='add_cookie_in_req', follow=True),
    ]

    def parse_product(self, response):
        yield from super().parse(response)

        yield from self.get_products(response)

    def add_cookie_in_req(self, request):
        request.cookies['tms_data'] = self.c
        return request

    def get_raw_product(self, response):
        return json.loads(response.css('#state::text').get())

    def get_products(self, response):
        raw = self.get_raw_product(response)
        p_info = raw['utag']['product']['productInfo']

        products, prices, = [], []
        p_ids = p_info['product_id']
        brands = p_info['product_brand']
        old_price_flags = p_info['product_pricing_adornment_flag']

        for i, values in enumerate(zip(p_ids, p_info['product_name'], brands,
                                       p_info['product_price'], old_price_flags)):
            product_id, name, brand, price, old_price_flag = values
            url, description, currency = '', '', ''
            images, old_prices = [], []

            item = NeimanItem()
            item['product_id'] = product_id
            item['name'] = name
            item['brand'] = brand if isinstance(brands, list) else brands

            if old_price_flag == 'true' or (old_price_flag == 'false' and len(p_ids) > 1):
                p = raw['productCatalog']['group']['childProducts'][product_id]
                url = p['linkedData']['url']
                currency = p['price']['currencyCode']
                description = p['linkedData']['description']
                images += self.get_media_images(p) + self.get_images(p)
                old_prices = [e['price'] for e in p['price'].get('adornments', []) if e['price'] != price]

            elif old_price_flag == 'false' and len(p_ids) == 1:
                p = raw['productCatalog']['product']
                currency = p['price']['currencyCode']
                raw_data = p['linkedData']
                description = raw_data['description']
                url = raw_data['url']
                images += self.get_media_images(p) + self.get_images(p)

            item['url'] = url
            item['image_urls'] = list(set(images))
            item['description'] = description
            # item['headers'] = response.headers

            products.append(item)
            prices.append(
                {
                    'price': price,
                    'old_prices': old_prices,
                    'currency': currency,
                },
            )

        self.get_skus(raw['utag']['product']['productAnalytics'], products, prices)

        return products

    def get_images(self, raw_product):
        urls = []
        raw_urls = raw_product['options']['productOptions']

        for raw in raw_urls:
            if raw.get('label') != 'color':
                continue

            for value in raw.get('values'):
                urls += self.get_media_images(value)

        return urls

    def get_media_images(self, raw_media):
        urls = []
        media = raw_media.get('media', {})
        alternates = media.get('alternate', {})
        url = media.get('main', {}).get('medium', {}).get('url')

        if url:
            urls.append(self.HTTPS + url)

        for e in alternates:
            url = alternates[e].get('medium', {}).get('url')
            if url:
                urls.append(self.HTTPS + url)

        return urls

    def get_skus(self, product_analytics, products, prices):
        for i, e in enumerate(product_analytics['details']['products']):
            skus = {}

            for s in e['skus']:
                sku = prices[i]
                sku['availability'] = s['inStock']
                sku['color'] = s['color']
                sku['size'] = s.get('size', 'one-size')
                skus[s['id']] = sku

            products[i].update(
                {
                    'skus': skus,
                },
            )
