# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class PostItem(scrapy.Item):
    thread_id = scrapy.Field()
    user_id = scrapy.Field()
    timestamp = scrapy.Field()
    message = scrapy.Field()
    quotes = scrapy.Field()
    post_no = scrapy.Field()
    # post_no is '2' in the last part of URL: http://metaldetectingforum.com/showpost.php?p=2499503&postcount=2
    # post_no is shown on upper right of each post container.

class UserItem(scrapy.Item):
    user_id = scrapy.Field()
    user_name = scrapy.Field()

class ThreadItem(scrapy.Item):
    thread_id = scrapy.Field()
    thread_name = scrapy.Field()
