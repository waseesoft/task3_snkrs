import re
import json

from scrapy.spiders import Spider, CrawlSpider, Rule, Request
from scrapy.linkextractors import LinkExtractor

from task3_snkrs.items import NeimanItem


class NeimanChina(Spider):
    name = 'neimanmarcus-china'
    HTTPS = 'https:'

    custom_settings = {
        'USER_AGENT': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36"
    }

    allowed_domains = [
        'neimanmarcus.com',
    ]

    start_urls = [
        # 'https://www.neimanmarcus.com/en-cn/index.jsp',
        # 'https://www.neimanmarcus.com/index.jsp',
        'https://www.neimanmarcus.com/en-cn/p/lagence-nina-printed-button-down-silk-blouse-prod225660067?parentId=cat68010736&icid=&searchType=EndecaDrivenCat&rte=%252Fcategory.jsp%253FitemId%253Dcat68010736%2526pageSize%253D30%2526No%253D0%2526refinements%253D&eItemId=prod225660067&xbcpath=cat000000_cat000730_cat68010736&cmCat=product',
        # 'https://www.neimanmarcus.com/p/brunello-cucinelli-look-prod223230027?childItemId=NMB4ZJZ_&focusProductId=prod221620191&navpath=cat000000_cat000001_cat44670744_cat25560734_cat39550741&page=1&position=40&uuid=PDP_PAGINATION_1dd1b8e90ecec73465664af77c5f86b3_c9HIcF7BlMVqgXS-GBWww4YdNxsCTSsa95621Nhh.jsession',
        # 'https://www.neimanmarcus.com/p/gentle-souls-demi-metallic-leather-comfort-slip-ons-prod224790337?childItemId=NMX4UTV_&navpath=cat000000_cat000141_cat47190746_cat75100734&page=0&position=0&uuid=PDP_PAGINATION_2825e87e85e7cb89a26b300bb01e0fd2_l-y6FcEjphd0dpr4JhRWZf3yJPqu4KasnPM9e_MH.jsession',
        # 'https://www.neimanmarcus.com/p/manolo-blahnik-hangisi-kitten-heel-satin-slingback-pumps-prod225750692?childItemId=NMX4VV7_&navpath=cat000000_cat000001_cat60840731_cat56520748_cat56520750&page=0&position=13&uuid=PDP_PAGINATION_5e0a04df07aef002b34d88babf6af500_KvRrD79vmlBqTAXqnh0zDshUSCaZ7y-S6g1vQKau.jsession'
        # 'https://www.neimanmarcus.com/p/eileen-fisher-half-sleeve-crepe-shift-dress-and-matching-items-prod212700005?childItemId=NMTWCYN_&focusProductId=prod205250295&navpath=cat000000_cat000001_cat58290731_cat43810733&page=0&position=11&uuid=PDP_PAGINATION_2e2b9cc440d0f6576b1edcd997c5b8d5_l-y6FcEjphd0dpr4JhRWZf3yJPqu4KasnPM9e_MH.jsession'
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

    product_req_cookie = {
        'tms_data': '{DT-2017.03}a3HwxssoiZzaMm5Pj2Bv6L13Gv8Ad/WZkJm2zLBiJ22quEI2eCcOen+zdhEJJvHeeOOXi+'
                    'MO99UjG2/1D+hl4AXI0xqxMcBJcNKRoDmB8W5Ptb0z0I9kIPIlYImXaHDdOdwGiYZVK7VYetLzT9+AlvcXA'
                    'gQLwm8YRoSydQX9y/iR/GCfWSi0wro7/kwt7J5Bi/FFkjSxBX6XHCkgroK52hUKgW/YC1MZ5sJseydRx1Ioi'
                    'HRiDZy5ztxXq6ZzvseaBT8nS56U9EH3crgXmw7726TvadPC383EPCcEAJZTuPTQi1SjH0Vww5owXy0GVtVTH'
                    'gQUbpz2HR2jg/liv8BYRgT2uIMscZUHtj+3+LXEgL6h5VNpAM7BXr6dpAo87UmpKZAaZhUufcW4Hj6OhLjcc5'
                    'Ae8ZOY/g3Ei3DxvzB6aoaOI4FwvVc1FhRMcX3UGkXfsYvcNKgQnb6ELb7f4yJm9mSzR3oVmqDMXFPe1HnsR95'
                    'VAvDwEZlbY18XLrU5bGYP4J/0xyiH9OE+PfysOstZsnMZxsPhNo1VZiWNo5S8enqzFf7dhClsTL5qAjscfQTNv'
                    '1JIrXORKfF6DcBf6i/91Q8zGK1KAKTv37mIV3btzFSeNu7fPUOTtBM/TFgJzzGLe7AYYInEvPqfxx0yQ+d5xzR'
                    'k7NNsgoykAQK83uIbFnVuJmCggiAv7tabslD7R/ZCKyfdbvFE1siLr8Lhn00KWEBdt9hvDuoEV1DiP+oaNg7B5'
                    'sIaxERI55GR2VgK/9C0UqiFyyO95itCF45/y/ruyNakse0Ttc80Q/BXLhImKOOi5HrGsbxf+PEuy5H84QG5/6Eh'
                    'XwB4UpWJQc82EysqOlMBhT/Jya6TmzWB9Ztp6jH4a2Wox15pF6VYlVHKTbLEIjmMZm1x+b3GYJaY0NPLNV8jeFLp'
                    'B3Tbs9RoUsHPbuN1gR29OXRa7GfW2oCg6AHm0/shfgNgeMf+9AsLDt7Mhg=='
    }

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, callback=self.parse, cookies=self.product_req_cookie)

    listings_css = [
        '.arrow-button--right',
        '.menu-wrapper a',
    ]

    rules = [
        Rule(LinkExtractor(restrict_css=listings_css), process_request='add_cookie_in_req'),
        Rule(LinkExtractor(restrict_css='.product-thumbnail__link'), callback='parse',
             process_request='add_cookie_in_req', follow=True),
    ]

    def parse(self, response):
        item = NeimanItem()
        item['product_id'] = self.get_id(response)

    def add_cookie_in_req(self, request):
        request.cookies['tms_data'] = self.product_req_cookie['tms_data']
        return request

    def get_raw_product(self, response):
        return json.loads(response.css('#state::text').get())

    def get_id(self, response):
        return ''

    def get_brand(self, response):
        return response.css('.product-heading__designer::text').getall()[0]

    def get_name(self, response):
        return response.css('.product-heading__name__product::text').getall()[0]

    def get_description(self, response):
        return response.css('.product-description__content__cutline-standard ::text').getall()

    def get_images(self, response):
        return response.css('.slick-slide.slick-active img::attr(src)').getall()

    def get_skus(self, response):
        skus = {}

        return skus

    def pricing(self, response):
        return {
            'previous_prices': '',
            'price': '',
            'currency': '',
        }

