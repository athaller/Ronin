# -*- coding: utf-8 -*-
from __future__ import absolute_import
import datetime
import json
import os
import sys

from scrapy import log
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from Ronin.items import RoninItem
from Ronin.utils import clean_text
from dateutil.parser import parse
from scrapy.conf import settings


class BollywoodSpider(CrawlSpider):
    name = "bollywood"
    rules = []

    def __init__(self, **kw):
        # get rules for the source
        self.domainSettings = self.read_rules_from_file(kw.get('source'))
        log.msg(self.domainSettings)
        # set allowed domains, start urls and xpaths of the site
        self.allowed_domains = self.domainSettings['allowed_domains']
        self.start_urls = self.domainSettings["start_urls"]
        self.xpath = self.domainSettings["xpaths"]
        self.cookies_seen = set()
        self.initialise_rules()
        # intitialise the parent class
        super(BollywoodSpider, self).__init__(**kw)

    def read_rules_from_file(self, source):
        # get the path for the rule file
        dir_path = os.path.join(settings['PROJECT_ROOT'], 'sites')
        path = os.path.join(dir_path, source + '.json')

        if os.path.isfile(path):
            with open(path) as data:
                return json.load(data)
        else:
            log.msg("unable to excess the rule file")
            sys.exit(0)

    def initialise_rules(self):
        # loop through every rules
        for rule in self.domainSettings["rules"]:
            allow_rule = ()
            if "allow" in rule.keys():
                allow_rule = [a for a in rule["allow"]]

            deny_rule = ()
            if "deny" in rule.keys():
                deny_rule = [d for d in rule["deny"]]

            restrict_xpaths_rule = ()
            if "restrict_xpaths" in rule.keys():
                restrict_xpaths_rule = [rx for rx in rule["restrict_xpaths"]]

            # Add rule to the class attribute
            BollywoodSpider.rules.append(Rule(
                SgmlLinkExtractor(
                    allow=allow_rule,
                    deny=deny_rule,
                    restrict_xpaths=restrict_xpaths_rule,
                ),
                follow=rule["follow"],
                callback='parse_item' if (
                    "use_content" in rule.keys()) else None
            ))

    def parse_item(self, response):
        """ Extract title, link, date, desc, keywords and the html text of a article,
        using XPath selectors
        """
        item = RoninItem()

        item['category'] = 'Bollywood'
        item['url'] = response.url
        item['title'] = response.xpath(self.xpath['title'][0]).extract()[0]

        # get the date of the article in format
        article_date = response.xpath(self.xpath['date'][0]).extract()
        try:
            item['date'] = str(parse(article_date[0].strip()))
        except Exception, e:
            print e
            if len(article_date) > 0:
                item['date'] = str(article_date[0].strip())
        item['images'] = response.xpath(self.xpath['image'][0]).extract()

        # content would be in different paragraph
        # loop over and extract each one of theme
        for expression in self.xpath['content']:
            content = response.xpath(expression).extract()
            if len(content) > 0:
                break
        item['content'] = clean_text(" ".join(content)).strip()
        item['timestamp'] = str(datetime.datetime.now())

        return item
