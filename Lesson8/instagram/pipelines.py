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

    def process_item(self, item):

        for i in item['username']:
            collection = self.mongobase[item['username']]
            filter_data = i
            update_data = {
                '$set': i
            }
            collection.update_one(filter_data, update_data, upsert=True)


        return item


class InstaPhotosPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['follower_photo_link']:
            try:
                yield scrapy.Request(item['follower_photo_link'])
            except Exception as e:
                print(e)

        if item['following_photo_link']:
            try:
                yield scrapy.Request(item['following_photo_link'])
            except Exception as e:
                print(e)

    def file_path(self, request, response=None, info=None, *, item=None):
        dir_name = item['username']
        if item['follower_name']:
            file_name = f'{item["follower_name"]}.jpg'
        elif item['following_name']:
            file_name = f'{item["following_name"]}.jpg'

        return f'full/{dir_name}/{file_name}'

    def item_completed(self, results, item, info):
        if results and item['follower_photo_link']:
            item['follower_photo_link'] = [itm[1] for itm in results if itm[0]]
        elif results and item['following_photo_link']:
            item['following_photo_link'] = [itm[1] for itm in results if itm[0]]

        return item
