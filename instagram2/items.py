# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class InstagramItem(scrapy.Item):
    # define the fields for your item here like:
    follower_name = scrapy.Field()
    follower_id = scrapy.Field()
    follower_photo_link = scrapy.Field()
    following_name = scrapy.Field()
    following_id = scrapy.Field()
    following_photo_link = scrapy.Field()
    username = scrapy.Field()