import logging
import requests
from lxml import etree
from urlparse import urljoin

from aleph.crawlers import Crawler, TagExists

log = logging.getLogger(__name__)

BUCKET = 'https://s3-eu-west-1.amazonaws.com/downloads.openoil.net/?prefix=contracts/'


class OpenOilCrawler(Crawler):

    DEFAULT_LABEL = "OpenOil Repository"
    DEFAULT_SITE = "http://repository.openoil.net/"

    def crawl(self):
        res = requests.get(BUCKET)
        doc = etree.fromstring(res.content)
        for key in doc.findall('.//Key'):
            if key.text.endswith('.zip'):
                continue
            url = urljoin(BUCKET, key.text)
            try:
                self.check_tag(url=url)
                self.emit_url(url)
            except TagExists:
                pass
