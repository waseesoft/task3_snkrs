import scrapy


class Item(scrapy.Item):
    item_id = scrapy.Field()
    name = scrapy.Field()
    brand = scrapy.Field()
    description = scrapy.Field()
    availability = scrapy.Field()
    currency = scrapy.Field()
    image_urls = scrapy.Field()
    skus = scrapy.Field()
    meta = scrapy.Field()
