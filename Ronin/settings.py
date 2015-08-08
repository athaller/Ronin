# -*- coding: utf-8 -*-

# Scrapy settings for Ronin project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

import os

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

BOT_NAME = 'Ronin'

SPIDER_MODULES = ['Ronin.spiders']
NEWSPIDER_MODULE = 'Ronin.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = 'Ronin (+http://www.yourdomain.com)'

# dynamoDB local config
DYNAMODB_HOST = 'localhost'
DYNAMODB_PORT = '8000'
TABLE_ARTICLES = 'ronin.dev.articles'
DYNAMODB_LOCAL = False

# dynamoDB config if deployed on EC2
DYNAMODB_REGION = 'us-east-1'
DYNAMODB_ENDPOINT = 'dynamodb.us-east-1.amazonaws.com'

DOWNLOAD_DELAY = 2

# ITEM_PIPELINES = {
#     'Ronin.pipelines.DynamoDBPipeline': 300
# }

# Somewhere in settings.py
# DUPEFILTER_CLASS = "Ronin.pipelines.BLOOMDupeFilter"

# Add extensions for webservice
EXTENSIONS = {
    'scrapy.contrib.corestats.CoreStats': 500,
    'scrapy.webservice.WebService': 500,
    'scrapy.telnet.TelnetConsole': 500,
}
