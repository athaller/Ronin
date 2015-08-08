import re
from scrapy import log


# Remove unicode, spaces and HTML tags
def clean_text(text):
    try:
        text = re.sub(
            ur'[\u064B-\u0652\u06D4\u0670\u0674\u06D5-\u06ED]+',
            '',
            text
        )
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'<[^>]*>', '', text)
        return text
    except Exception, e:
        log.msg("Unable to process the text {0}".format(e))

