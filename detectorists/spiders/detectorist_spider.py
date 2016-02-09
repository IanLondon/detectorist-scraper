import scrapy
import re
from detectorists.processors import to_int
from detectorists.items import PostItem, UserItem, ThreadItem
import logging


# This is a vBulletin forum, I wonder if all of them have similar XPath selection targets???

class DetectoristSpider(scrapy.Spider):
    name = 'detectorist'
    allowed_domains = ['metaldetectingforum.com']
    start_urls = ["http://metaldetectingforum.com"]

    # Thread ID 12345 would look like: 'http://example.com/showthread.php?t=12345...'
    patterns = {'thread_id': re.compile('t=(\d+)'),
    'next_page_url': "//*[@class='pagenav']//*[@href and contains(text(), '>')]/@href" }

    def paginate(self, response, next_page_callback):
        """Returns a scrapy.Request for the next page, or returns None if no next page found.
        response should be the Response object of the current page."""
        # This gives you the href of the '>' button to go to the next page
        # There are two identical ones with the same XPath, so just extract_first.
        next_page = response.xpath(self.patterns['next_page_url'])

        if next_page:
            url = response.urljoin(next_page.extract_first())
            logging.info("NEXT PAGE IS: %s" % url)
            return scrapy.Request(url, next_page_callback)
        else:
            logging.info("NO MORE PAGES FOUND")
            return None

    def parse(self, response):
        # Parse the board (aka index) for forum URLs
        forum_urls = response.xpath('.//td[contains(@id,"f")]/div/a/@href').extract()
        for url in forum_urls:
            yield scrapy.Request(response.urljoin(url), callback=self.parse_forum)

    def parse_forum(self, response):
        logging.info("STARTING NEW FORUM SCRAPE (GETTING THREADS)")
        thread_urls = response.xpath('.//a[contains(@id,"thread_title")]/@href').extract()
        for url in thread_urls:
            yield scrapy.Request(response.urljoin(url), callback=self.parse_posts)

        # return the next forum page if it exists
        yield self.paginate(response, next_page_callback=self.parse_forum)


    def parse_posts(self, response):
        logging.info("STARTING NEW PAGE SCRAPE")

        # Get info about thread
        # TODO: move this into parse_forum, b/c here the code runs every page of the thread
        thread = ThreadItem()
        thread['thread_id'] = to_int(re.findall(self.patterns['thread_id'], response.url)[0])
        thread['thread_name'] = response.xpath('.//meta[@name="twitter:title"]/@content').extract_first()
        thread['thread_path'] = response.xpath('.//div/table//tr/td/table//tr/td[3]//a/text()').extract()


        # Scrape all the posts on a page for post & user info
        for post in response.xpath("//table[contains(@id,'post')]"):
            p = PostItem()

            p['thread_id'] = thread['thread_id']
            p['user_id'] = to_int(post.xpath(".//a[@class='bigusername']/@href").re_first('u=(\d+)'))
            p['timestamp'] = post.xpath("string(.//tr/td/div[@class='normal'][2])").extract_first().strip()
            p['quotes'] = post.xpath('.//blockquote/text()').extract()

            # Message text, excluding blockquotes
            # Also excluding the <div> that has user "signatures"
            # (perhaps later on for NLP you'd want to insert a BLOCKQUOTE word-marker)
            p['message'] = post.xpath(".//*[contains(@id,'post_message_')]//text()[not(parent::blockquote)]").extract()

            p['post_no'] = to_int(post.xpath(".//tr/td/div[@class='normal'][1]/a//text()").extract_first())

            # user info
            user = UserItem()
            user['user_id'] = p['user_id']
            user['user_name'] = post.xpath(".//a[@class='bigusername']//text()").extract_first()

            yield p
            yield user

        yield thread

        # Pagination across thread: search for the link that the next button '>' points to, if any
        # next_page_request = self.paginate(next_page_callback=self.parse_posts)
        # if next_page_request:
            # yield next_page_request
        # WARNING TODO just trying this, it might be None
        yield self.paginate(response, next_page_callback=self.parse_posts)



# Post container: use this for each post
# //table[contains(@id,'post')]

# Name (<a> with link to member page): ... /a[@class='bigusername']
# Get member page link URL with:
# ... a[@class='bigusername']/@href

# You could get name text with
# ... a[@class='bigusername']/text()
# you could also use userid to look up info later...

# Post messages:
# ... [contains(@id,'post_message_')]

# Post timestamp
# ... /tr/td/div[@class='normal'][2]

# Post number
# ... tr/td/div[@class='normal'][1]/a
