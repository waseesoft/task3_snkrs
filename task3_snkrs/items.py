from scrapy import Item, Field


class OrsayItem(Item):
    product_id = Field()
    name = Field()
    brand = Field()
    description = Field()
    image_urls = Field()
    skus = Field()
    meta = Field()
