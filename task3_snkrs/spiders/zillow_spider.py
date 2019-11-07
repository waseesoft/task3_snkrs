import json
from datetime import datetime, timedelta

from scrapy import Request
from scrapy.spiders import SitemapSpider

from zillow.items import ZillowItem


class ZillowSpider(SitemapSpider):
    name = 'zillow'
    QUERY_ID = '16b16ec9c5b3bc27ad53eaca3d0faf74'
    OPERATION_NAME = 'ForSaleDoubleScrollFullRenderQuery'
    PRODUCTS_REQ_BASE_URL = 'https://www.zillow.com/graphql/'
    country_website_template = 'https://www.zillow.com/CountyAssessorPage.htm?' \
                               'COUNTY_ID=%s&FORCE_GENERIC=false&LINK_LOCATION=' \
                               'description&PARCEL_NUM=%s'

    products_req_headers = {
        'content-type': 'text/plain',
        'accept': '*/*',
        'authority': 'www.zillow.com',
    }

    allowed_domains = [
        'zillow.com',
        'zillowstatic.com',
    ]

    sitemap_urls = [
        'https://www.zillow.com/sitemap/catalog/cdp/index.xml',
    ]

    def parse(self, response):
        urls_s = response.css('.ListCardSet__StyledList-sc-16r7gf2-0 a')
        return [response.follow(url_s, callback=self.parse_products)
                for url_s in urls_s]

    def parse_products(self, response):
        zpid = self.get_product_id(response)
        status = response.css('.zsg-tooltip-launch_keyword::text,'
                              ' .ds-status-details::text').get()

        params = {
            "operationName": self.OPERATION_NAME,
            "variables": {"zpid": zpid, "contactFormRenderParameter":
                {"zpid": zpid, "platform": "desktop", "isDoubleScroll": True}},
            "clientVersion": "home-details/5.45.5.0.master.63051cd",
            "queryId": self.QUERY_ID,
        }

        return Request(self.PRODUCTS_REQ_BASE_URL, callback=self.parse_product,
                       method='POST', body=json.dumps(params), meta={'status': status},
                       headers=self.products_req_headers, dont_filter=True)

    def parse_product(self, response):
        raw_property = self.get_property(response)
        fact_map = self.get_fact_map(raw_property)

        item = ZillowItem()
        item['status'] = response.meta['status']
        item['beds'] = self.get_beds(fact_map)
        item['baths'] = self.get_baths(raw_property)
        item['livable_sqft'] = raw_property['livingArea'] or ''
        item['type'] = raw_property.get('homeType')
        item['year_built'] = raw_property['yearBuilt']
        item['heating'] = self.get_heating(fact_map)
        item['cooling'] = self.get_cooling(fact_map)
        item['parking'] = self.get_parking(fact_map)
        item['lot_sqft'] = raw_property['lotSize'] or -1
        item['bedroom_count'] = self.get_bedrooms_count(fact_map)
        item['stories'] = self.get_stories(fact_map)
        item['external_materials'] = self.get_external_materials(fact_map)
        item['foundation_type'] = self.get_foundation_type(fact_map)
        item['roof'] = self.get_roof(fact_map)
        item['pool'] = self.get_pool(raw_property)
        item['garage_yn'] = self.get_garage_yn(raw_property)
        item['hoa_fee'] = self.get_hoa_fee(raw_property)
        item['last_sold_date'] = self.get_last_sold_date(raw_property)
        item['last_sold_price'] = self.get_last_sold_price(raw_property)
        item['listed_for_sale'] = self.get_listed_for_sale(raw_property)
        item['listing_price'] = raw_property['price']
        item['rental_amount'] = raw_property['rentZestimate']
        item['parcel'] = raw_property['parcelId']
        item['zestimate'] = raw_property['zestimate']
        item['rent_zestimate'] = raw_property['rentZestimate']
        item['tax_history'] = self.get_tax_history(raw_property)
        item['schools'] = self.get_schools(raw_property)
        item['country_website'] = self.get_country_website(raw_property)

        yield item

    def get_property(self, response):
        return json.loads(response.text)['data']['property']

    def get_product_id(self, response):
        css = '#hdpApolloPreloadedData::text'
        return json.loads(response.css(css).get())['zpid']

    def get_beds(self, fact_map):
        return self.map(fact_map, 'beds')

    def get_baths(self, raw_property):
        baths_detail = f'{raw_property["resoFacts"]["bathroomsFull"] or 0} full'
        baths_detail += f' {raw_property["resoFacts"]["bathroomsHalf"] or 0} half'

        return f'{raw_property["bathrooms"]} ({baths_detail})'

    def get_heating(self, fact_map):
        return self.map(fact_map, 'heating') or 'No Data'

    def get_cooling(self, fact_map):
        return self.map(fact_map, 'cooling') or 'No Data'

    def get_parking(self, fact_map):
        return self.map(fact_map, ['parking', 'parkingfeatures']) or 'No Data'

    def get_bedrooms_count(self, fact_map):
        return self.map(fact_map, ['room count'])

    def get_stories(self, fact_map):
        return self.map(fact_map, 'stories')

    def get_external_materials(self, fact_map):
        return self.map(fact_map, 'exterior material')

    def get_foundation_type(self, fact_map):
        return self.map(fact_map, 'foundation type')

    def get_roof(self, fact_map):
        return self.map(fact_map, ['roof type', 'roof'])

    def get_pool(self, raw_property):
        return 'Yes (Private: Pool)' \
            if raw_property['resoFacts']['hasPrivatePool'] else 'No'

    def get_garage_yn(self, raw_property):
        return 'Yes' if raw_property['resoFacts']['hasGarage'] else 'No'

    def get_hoa_fee(self, raw_property):
        return raw_property['hoaFee'] if raw_property['hoaFee'] else 'No'

    def get_last_sold_date(self, raw_property):
        date = [datetime.fromtimestamp(e['time'] // 1e3).strftime('%d/%m/%Y') for e
                in raw_property['priceHistory'] if e['event'].lower() in ['sold']]
        return date[0] if date else ''

    def get_last_sold_price(self, raw_property):
        price = [e['price'] for e in raw_property['priceHistory']
                 if e['event'].lower() in ['sold']]
        return price[0] if price else ''

    def get_listed_for_sale(self, raw_property):
        dt = datetime.today() - timedelta(days=raw_property['daysOnZillow'] or 0)
        return dt.strftime('%d/%m/%Y')

    def get_tax_history(self, raw_property):
        tax_history = []
        for th in raw_property['taxHistory']:
            tax_history.append({
                'year': datetime.fromtimestamp(th['time'] // 1e3).year,
                'Property Taxes': th['taxPaid'] or '--',
                'Tax Assessment': th['value'] or '--'
            })

        return tax_history or 'Tax history is unavailable.'

    def get_schools(self, raw_property):
        return [{'name': sc['name'], 'grades': sc['grades'],
                 'value': sc['rating']} for sc in raw_property['schools']] or ''

    def get_country_website(self, raw_property):
        return self.country_website_template % \
               (raw_property['countyFIPS'], raw_property['parcelId']) \
                if raw_property['countyFIPS'] and raw_property['parcelId'] else ''

    def get_fact_map(self, raw_property):
        category_details = raw_property['homeFacts']['categoryDetails']
        return {cf['factLabel']: cf['factValue'] for cd in category_details
                 for cat in cd['categories'] for cf in cat['categoryFacts']}

    def map(self, fact_map, fact_label):
        for fk, fv in fact_map.items():
            if str(fk).lower() in fact_label:
                return fv

        return ''
