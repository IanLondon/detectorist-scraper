# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


# class DetectoristsPipeline(object):
#     def process_item(self, item, spider):
#         return item

import pymongo

# Adapted from
# http://doc.scrapy.org/en/stable/topics/item-pipeline.html#write-items-to-mongodb

class MongoPipeline(object):

    post_collection = 'posts'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'items')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        # just process posts for now
        # TODO: process user items with different collection
        self.db[self.post_collection].insert(dict(item))
        return item
