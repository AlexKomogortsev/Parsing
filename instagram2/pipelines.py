# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import scrapy
from scrapy.pipelines.images import ImagesPipeline
from pymongo import MongoClient


class InstagramPipeline:

    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongobase = client.Instagram

    def process_item(self, item, *args, **kwargs):
        collection = self.mongobase[item['username']]
        filter_data = item
        update_data = {
            '$set': item
        }
        collection.update_one(filter_data, update_data, upsert=True)

        return item


class InstaPhotosPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if 'follower_photo_link' in item.keys():
            return scrapy.Request(item['follower_photo_link'])
        elif 'following_photo_link' in item.keys():
            return scrapy.Request(item['following_photo_link'])


    def file_path(self, request, response=None, info=None, *, item=None):
        dir_name = item['username']
        if 'follower_photo_link' in item.keys():
            key = 'follower_name'
        elif 'following_photo_link' in item.keys():
            key = 'following_name'

        file_name = f'{item[key]}.jpg'
        return f'full/{dir_name}/{file_name}'

    def item_completed(self, results, item, info):
        if 'follower_photo_link' in item.keys():
            key = 'follower_photo_link'
        elif 'following_photo_link' in item.keys():
            key = 'following_photo_link'

        item[key] = results[0][1]

        return item
