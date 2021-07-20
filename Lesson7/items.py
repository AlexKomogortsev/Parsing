# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import MapCompose, TakeFirst


class LeroyItem(scrapy.Item):
    name = scrapy.Field(output_processor=TakeFirst())
    photos = scrapy.Field()
    params = scrapy.Field()
    link = scrapy.Field(output_processor=TakeFirst())
    char_types = scrapy.Field()
    char_desc = scrapy.Field()
    price = scrapy.Field(output_processor=TakeFirst())
    _id = scrapy.Field()
