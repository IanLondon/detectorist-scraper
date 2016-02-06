import scrapy

from detectorists.items import ForumThreadItem

class DetectoristSpider(scrapy.Spider):
    name = 'detectorist'
    allowed_domains = ['http://metaldetectingforum.com']
    start_urls = ["http://metaldetectingforum.com/showthread.php?t=226343"]

    def parse(self, response):
        for post in response.xpath("//table[contains(@id,'post')]"):
            t = ForumThreadItem()

            t['user_id'] = post.xpath(".//a[@class='bigusername']/@href").re('u=(\d+)')[0]
            t['timestamp'] = post.xpath("string(.//tr/td/div[@class='normal'][2])").extract()[0].strip()
            t['message'] = post.xpath(".//*[contains(@id,'post_message_')]/text()").extract()[0].strip()
            t['post_no'] = post.xpath(".//tr/td/div[@class='normal'][1]/a//text()").extract()[0]

            yield t

        # Search for the link that the next button '>' points to, if any
        rel_next_page = response.xpath("//*[@class='pagenav']//*[@href and contains(text(), '>')]/@href").extract()[0]

        next_page = response.urljoin(rel_next_page)
        print "next page is ", next_page


# Post container: use this for each post
# //table[contains(@id,'post')]

# Name (<a> with link to member page): ... /a[@class='bigusername']
# Get member page link URL with:
# ... a[@class='bigusername']/@href

# You could get name text with
# ... a[@class='bigusername']/text()
# but don't! Use userid to look up info later...

# Post messages:
# ... [contains(@id,'post_message_')]

# Post timestamp
# ... /tr/td/div[@class='normal'][2]

# Post number
# ... tr/td/div[@class='normal'][1]/a
