import scrapy
from scrapy import Request
from task3_snkrs.items import NeimanItem
import json
import base64


class NeimanmarcusSpider(scrapy.Spider):
    name = 'test-spider'
    allowed_domains = ['neimanmarcus.com']
    base_url = 'https://www.neimanmarcus.com/'
    image_base_url = 'http://neimanmarcus.scene7.com/is/image/NeimanMarcus/'
    start_urls = ['https://www.neimanmarcus.com/en-cn/c/designers-cat000730?siloId='
                  'cat000730&navid=topNavDesigners&navpath=cat000000_cat000730']
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0'}

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, headers=self.headers)

    def parse(self, response):
        designers = response.xpath('//div[@class="designerlink"]//a[@itemprop="significantLink"]'). \
            css('::attr(href)').getall()

        #designers = '/en-cn/c/designers-eileen-fisher-cat000045?navAction=index&seoCategoryName=&navpath=cat000000_cat000730_cat000045&seoDesignerName=Eileen+Fisher'
        for url in designers:
            yield response.follow(url, callback=self.parse_product_page, headers=self.headers)

    def parse_product_page(self, response):
        products_category = response.xpath('//ul[@class="category-menu"]//a[@id="rootcatnav"] | '
                                           '//ul[@class="category-menu"]//a[@class="  navLastItem"]').css(
            '::attr(href)').getall()

        for url in products_category:
            yield response.follow(url, callback=self.parse_products, headers=self.headers)

    def parse_products(self, response):
        products_exist = response.css('#productTemplateId').css('::attr(href)').getall()
        if len(products_exist) != 0:
            product_urls = response.css('#productTemplateId').css('::attr(href)').getall()
            for url in product_urls:
                yield response.follow(url, callback=self.get_product_data, headers=self.headers)

    def get_product_data(self, response):
        prod_id = self.get_product_id(response)
        encoded_id = str(base64.b64encode(prod_id.encode("utf-8")).decode("utf-8"))
        frmdata = {
            'data': '$b64$eyJQcm9kdWN0U2l6ZUFuZENvbG9yIjp7InByb2R1Y3RJZHMiOiJwcm9k' + str(encoded_id) + 'In19',
            'sid': 'getSizeAndColorData',
            'bid': 'ProductSizeAndColor',
            'timestamp': '1570532911316'
        }
        url = 'https://www.neimanmarcus.com/en-cn/product.service?instart_disable_injection=True'
        yield scrapy.http.FormRequest(url, callback=self.parse_data, formdata=frmdata, headers=self.headers,
                                      meta={'response': response})

        next_page = response.css('.pagination a.nextpage').css('::attr(href)').get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.get_product_data, headers=self.headers)

    def parse_data(self, response):
        json_data = json.loads(response.text)
        prod_detail = response.meta['response']
        item = NeimanItem()
        item['brand'] = self.get_brand_name(prod_detail)
        item['description'] = self.get_description(prod_detail)
        item['product_id'] = self.get_product_id(prod_detail)
        item['name'] = self.get_product_name(prod_detail)
        item['image_urls'] = self.get_image_urls(prod_detail)
        skus_data = json.loads(json_data['ProductSizeAndColor']['productSizeAndColorJSON'])
        req_data = skus_data[0]['skus']
        item['skus'] = self.get_skus(prod_detail, req_data)
        return item


    def get_brand_name(self, response):
        return response.css('.product-designer a').css('::text').get()

    def get_product_id(self, response):
        prod_id = response.css('.itemIdHidden').css('::attr(value)').get()
        p_id = ''.join(i for i in prod_id if i.isdigit())
        return p_id

    def get_product_name(self, response):
        return response.css('.prodDisplayName').css('::text').get()

    def get_description(self, response):
        return response.css('.productCutline li').css('::text').getall()

    def get_image_urls(self, response):
        image_url_data = response.css('#color-pickers .color-picker').css('::attr(data-sku-img)').getall()
        image_urls = response.css('.product-thumbnail').css('::attr(src)').getall()

        for data in image_url_data:
            json_acceptable_string = data.replace("'", "\"")
            parsed_link = json.loads(json_acceptable_string)
            print(parsed_link['a*'])
            image_urls.append(self.image_base_url + parsed_link['a*'])
            image_urls.append(self.image_base_url + parsed_link['m*'])

        print(image_urls)
        return image_urls

    def get_skus(self, response, req_data):
        skus = {}

        for data in req_data:
            sku = self.get_price_detail(response)
            sku['color'] = data['color'].split('?')[0]
            sku['available'] = data['status']
            sku['size'] = data['size']
            skus[data['sku']] = sku

        return skus

    def get_price_detail(self, response):
        sku = {
            "current_price": self.get_current_price(response),
            "old_price": self.get_old_price(response),
            "currency": self.get_currency(response),
        }
        return sku

    def get_current_price(self, response):
        price = response.xpath('//div[@class="price-adornments-elim-suites"]//span[@class="pos1override item-price"] '
                               '| //p[@class="lbl_ItemPriceSingleItem product-price"]').css('::text').get().strip()
        final_price = price.split(' ')
        return final_price[1]

    def get_old_price(self, response):
        price = response.xpath('//div[@class="price-adornments-elim-suites"]//span[@class="item-price"] | //p['
                               '@class="lbl_ItemPriceSingleItem product-price"]').css('::text').get().strip()
        final_price = price.split(' ')
        return final_price[1]

    def get_currency(self, response):
        price = response.xpath('//div[@class="price-adornments-elim-suites"]//span[@class="item-price"] | //p['
                               '@class="lbl_ItemPriceSingleItem product-price"]').css('::text').get().strip()
        final_price = price.split(' ')
        return final_price[0]