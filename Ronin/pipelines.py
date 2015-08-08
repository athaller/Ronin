# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import re
import random
import base64
import os
from boto.dynamodb2.table import Table

from scrapy import log
from scrapy.exceptions import DropItem
from scrapy.conf import settings
from scrapy.utils.job import job_dir
from scrapy.dupefilter import BaseDupeFilter

from pybloom import BloomFilter
from boto.dynamodb2.layer1 import DynamoDBConnection
from boto.dynamodb2.table import Table


class RoninPipeline(object):
    def process_item(self, item, spider):
        return item


# create dynamodb connection
# @local: dynamodb hosted on local server or not
def get_dynamo_db_connection(local=False):
    if local:
        db = DynamoDBConnection(
            host=settings['DYNAMODB_HOST'],
            port=settings['DYNAMODB_PORT'],
            aws_secret_access_key='spiderman',
            aws_access_key_id='spiderman',
            is_secure=False)
    else:
        params = {
            'is_secure': True
        }
        # Read from scrapy settings, if provided
        params['region'] = settings['DYNAMODB_REGION']
        params['host'] = settings['DYNAMODB_ENDPOINT']
        params['aws_access_key_id'] = os.environ.get('AWS_ACCESS_KEY_ID')
        params['aws_secret_access_key'] = os.environ.get('AWS_SECRET_ACCESS_KEY')

        db = DynamoDBConnection(**params)
    return db


class DynamoDBPipeline(object):
    def __init__(self):
        self.db = get_dynamo_db_connection()
        try:
            self.article_table = Table(
                settings['TABLE_ARTICLES'], connection=self.db)
        except Exception, e:
            log.msg("Article Table doesn't exits {0}".format(e),
                    level=log.CRITICAL)

    def process_item(self, item, spider):
        valid = True
        ignore_keys = ['images']
        for key, value in item.iteritems():
            # here we only check if the data is not null
            # but we could do any crazy validation we want
            if key in ignore_keys:
                continue

            if not value:
                valid = False
                raise DropItem(
                    "Missing %s of website from %s"
                    % (key, item['url'])
                )
        if valid:
            print item
            self.article_table.put_item(data=dict(item))
            log.msg("Item written to DynamoDB database %s" %
                    (settings['DYNAMODB_TABLE']),
                    level=log.DEBUG, spider=spider)
        return item

    def get_url_list(self):
        articles = self.article_table.scan()
        urllist = list()
        for article in articles:
            urllist.append(article['url'])
        return urllist



class BLOOMDupeFilter(BaseDupeFilter):
    """Request Fingerprint duplicates filter"""

    def __init__(self, path=None):
        self.file = None
        # capacity
        #     this BloomFilter must be able to store at least *capacity* elements
        #     while maintaining no more than *error_rate* chance of false
        #     positives
        # error_rate
        #     the error_rate of the filter returning false positives. This
        #     determines the filters capacity. Inserting more than capacity
        #     elements greatly increases the chance of false positives.
        self.fingerprints = BloomFilter(capacity=2000000, error_rate=0.00001)
        # get all the urls from database
        db = DynamoDBPipeline()
        urls = db.get_url_list()
        [self.fingerprints.add(url) for url in urls]

    @classmethod
    def from_settings(cls, settings):
        return cls(job_dir(settings))

    def request_seen(self, request):
        fp = request.url
        if fp in self.fingerprints:
            return True
        self.fingerprints.add(fp)

    def close(self, reason):
        self.fingerprints = None


class RandomProxy(object):
    def __init__(self, settings):
        self.proxy_list = settings.get('PROXY_LIST')
        fin = open(self.proxy_list)

        self.proxies = {}
        for line in fin.readlines():
            parts = re.match('(\w+://)(\w+:\w+@)?(.+)', line)

            # Cut trailing @
            if parts.group(2):
                user_pass = parts.group(2)[:-1]
            else:
                user_pass = ''

            self.proxies[parts.group(1) + parts.group(3)] = user_pass

        fin.close()

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_request(self, request, spider):
        # Don't overwrite with a random one (server-side state for IP)
        if 'proxy' in request.meta:
            return

        proxy_address = random.choice(self.proxies.keys())
        proxy_user_pass = self.proxies[proxy_address]

        request.meta['proxy'] = proxy_address
        if proxy_user_pass:
            basic_auth = 'Basic ' + base64.encodestring(proxy_user_pass)
            request.headers['Proxy-Authorization'] = basic_auth

    def process_exception(self, request, exception, spider):
        proxy = request.meta['proxy']
        log.msg('Removing failed proxy <%s>, %d proxies left' % (
                    proxy, len(self.proxies)))
        try:
            del self.proxies[proxy]
        except ValueError:
            pass

