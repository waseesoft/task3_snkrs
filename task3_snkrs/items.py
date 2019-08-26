from scrapy import Item, Field


class SnkrsItem(Item):
    item_id = Field()
    name = Field()
    brand = Field()
    description = Field()
    image_urls = Field()
    skus = Field()
