# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


# class DetectoristsPipeline(object):
#     def process_item(self, item, spider):
#         return item

import pymongo
from scrapy.exceptions import DropItem
from detectorists.items import PostItem, UserItem, ThreadItem

# Adapted from
# http://doc.scrapy.org/en/stable/topics/item-pipeline.html#write-items-to-mongodb

class MongoPipeline(object):

    # collection_map = {PostItem:'posts',
    #                   UserItem:'users',
    #                   ThreadItem: 'threads'}

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
        # first, screen for duplicates
        filter_dict = {key: item[key] for key in item if key in item.unique_fields}

        if self.db[item.collection].count(filter_dict) > 0:
            raise DropItem("Duplicate item found: %s. Filter was %s" % (item, filter_dict))
        else:
            # not a duplicate, add it
            self.db[item.collection].insert(dict(item))
        return item
