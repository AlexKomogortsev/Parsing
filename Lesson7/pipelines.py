# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import scrapy
from itemadapter import ItemAdapter
from scrapy.pipelines.images import ImagesPipeline
import hashlib


class LeroyPipeline:
    def process_item(self, item, spider):
        if item['price'] is not None:
            item['price'] = float(item['price'].replace(" ", ""))

        item['params'] = {x: y for x, y in list(zip(item['char_types'], item['char_desc']))}

        for key, val in item['params'].items():
            item['params'][key] = val.split('\n                ')[1]

        del item['char_types']
        del item['char_desc']

        return item

    # def get_params(self, item):
    #     if item['all_params']:
    #         for param in item['all_params']:
    #             type =


class LeroyPhotosPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['photos']:
            for img in item['photos']:
                try:
                    yield scrapy.Request(img)
                except Exception as e:
                    print(e)


    def item_completed(self, results, item, info):
        if results:
            item['photos'] = [itm[1] for itm in results if itm[0]]
        return item
