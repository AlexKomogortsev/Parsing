# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient


class BookparserPipeline:

    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongobase = client.Books

    def process_item(self, item, spider):

        if spider.name == 'labirint':
            if item['price_init'] is not None:
                item['price_init'] = int(item['price_init'])
            if item['price_new'] is not None:
                item['price_new'] = int(item['price_new'])
            if item['rating'] is not None:
                item['rating'] = float(item['rating'])

        if spider.name == 'books24':
            if len(item['author']) > 0:
                item['author'] = item['author'][-1].split('\n')[1]
            if item['title'] is not None:
                item['title'] = item['title'][-1].split('\n        ')[1]
            if item['price_init'] is not None:
                item['price_init'] = item['price_init'].split('\n  ')[1]
            if item['price_new'] is not None:
                item['price_new'] = item['price_new'].split('\n  ')[1]
            if item['rating'] is not None:
                item['rating'] = item['rating'].split('\n      ')[1]

        collection = self.mongobase[spider.name]
        filter_data = item
        update_data = {
            '$set': item
        }
        collection.update_one(filter_data, update_data, upsert=True)

        return item
