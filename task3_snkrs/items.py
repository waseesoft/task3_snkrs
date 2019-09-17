from scrapy.item import Field, Item


class SnkrsItem(Item):
    item_id = Field()
    name = Field()
    brand = Field()
    description = Field()
    image_urls = Field()
    skus = Field()


class LanebryantItem(Item):
    product_id = Field()
    name = Field()
    brand = Field()
    description = Field()
    image_urls = Field()
    skus = Field()
    url = Field()
    headers = Field()
    meta = Field()


class NeimanItem(Item):
    product_id = Field()
    name = Field()
    brand = Field()
    description = Field()
    image_urls = Field()
    skus = Field()
    url = Field()
    headers = Field()
    meta = Field()


class ZillowItem(Item):
    status = Field()
    beds = Field()
    baths = Field()
    livable_sqft = Field()
    type = Field()
    year_built = Field()
    heating = Field()
    cooling = Field()
    parking = Field()
    lot_sqft = Field()
    bedroom_count = Field()
    stories = Field()
    external_materials = Field()
    foundation_type = Field()
    roof = Field()
    pool = Field()
    garage_yn = Field()
    hoa_fee = Field()
    last_sold_date = Field()
    last_sold_price = Field()
    listed_for_sale = Field()
    listing_price = Field()
    rental_amount = Field()
    parcel = Field()
    zestimate = Field()
    rent_zestimate = Field()
    tax_history = Field()
    schools = Field()
    country_website = Field()
