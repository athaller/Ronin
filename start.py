"""
run scrapers programmatically from a script
"""
from Ronin.spiders.roninspider import BollywoodSpider

# scrapy api
from scrapy import signals, log
from twisted.internet import reactor
from scrapy.crawler import Crawler
# from scrapy.settings import Settings
from scrapy.utils.project import get_project_settings


# list of crawlers
TO_CRAWL = ['filmfare', 'indicine', 'bollywoodhungama']
# list of crawlers that are running
RUNNING_CRAWLERS = []


def spider_closing(spider):
    """Activates on spider closed signal"""
    log.msg("Spider closed: %s" % spider, level=log.INFO)
    RUNNING_CRAWLERS.remove(spider)
    if not RUNNING_CRAWLERS:
        reactor.stop()

log.start(loglevel=log.DEBUG)
for source in TO_CRAWL:
    settings = get_project_settings()
    # crawl responsibly
    settings.set("USER_AGENT", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) \
     AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.65 Safari/537.36")
    crawler = Crawler(settings)
    crawler_obj = BollywoodSpider(source=source)
    RUNNING_CRAWLERS.append(crawler_obj)
    # stop reactor when spider closes
    crawler.signals.connect(spider_closing, signal=signals.spider_closed)
    crawler.configure()
    crawler.crawl(crawler_obj)
    crawler.start()

# blocks process so always keep as the last statement
reactor.run()
