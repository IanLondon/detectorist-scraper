import scrapy
import re
from detectorists.items import PostItem, UserItem, ThreadItem

# This is a vBulletin forum, I wonder if all of them have similar XPath selection targets???

class DetectoristSpider(scrapy.Spider):
    name = 'detectorist'
    allowed_domains = ['metaldetectingforum.com']
    start_urls = ["http://metaldetectingforum.com/showthread.php?t=226343"]

    # Thread ID 12345 would look like: 'http://example.com/showthread.php?t=12345...'
    patterns = {'thread_id': re.compile('t=(\d+)') }

    def parse(self, response):
        print "STARTING NEW PAGE SCRAPE"

        # Get info about thread
        thread = ThreadItem()
        thread['thread_id'] = int(re.findall(self.patterns['thread_id'], response.url)[0])
        thread['thread_name'] = response.xpath('.//meta[@name="twitter:title"]/@content').extract_first()

        # Scrape all the posts on a page for post & user info
        for post in response.xpath("//table[contains(@id,'post')]"):
            p = PostItem()

            p['thread_id'] = thread['thread_id']
            p['user_id'] = int(post.xpath(".//a[@class='bigusername']/@href").re_first('u=(\d+)'))
            p['timestamp'] = post.xpath("string(.//tr/td/div[@class='normal'][2])").extract_first().strip()
            p['quotes'] = post.xpath('.//blockquote/text()').extract()

            # Message text, excluding blockquotes
            # Also excluding the <div> that has user "signatures"
            # (perhaps later on for NLP you'd want to insert a BLOCKQUOTE word-marker)
            p['message'] = post.xpath(".//*[contains(@id,'post_message_')]//text()[not(parent::blockquote)]").extract()

            p['post_no'] = post.xpath(".//tr/td/div[@class='normal'][1]/a//text()").extract_first()

            # user info
            user = UserItem()
            user['user_id'] = p['user_id']
            user['user_name'] = post.xpath(".//a[@class='bigusername']//text()").extract_first()

            yield p
            yield user

        yield thread

        # Pagination across thread: search for the link that the next button '>' points to, if any
        next_page = response.xpath("//*[@class='pagenav']//*[@href and contains(text(), '>')]/@href")

        if next_page:
            url = response.urljoin(next_page[0].extract())
            print "NEXT PAGE IS: ", url
            yield scrapy.Request(url, self.parse)
        else:
            print "NO MORE PAGES FOUND"


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
