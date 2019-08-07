import scrapy


class Task3SnkrsItem(scrapy.Item):
    product_id = scrapy.Field()
    name = scrapy.Field()
    brand = scrapy.Field()
    description = scrapy.Field()
    availability = scrapy.Field()
    currency = scrapy.Field()
    image_urls = scrapy.Field()
    old_prices = scrapy.Field()
    new_price = scrapy.Field()
    sizes = scrapy.Field()
    skus = scrapy.Field()
    sku_id = scrapy.Field()
