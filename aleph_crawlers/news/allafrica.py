import logging
import requests
from lxml import html
from urlparse import urljoin

from aleph.crawlers import Crawler, TagExists

log = logging.getLogger(__name__)


class AllAfricaCrawler(Crawler):

    DEFAULT_LABEL = "AllAfrica"
    DEFAULT_SITE = "http://allafrica.com/"

    def crawl(self):
        url_base = 'http://allafrica.com/latest/?page=%s'
        for i in xrange(1, 1000):
            url = url_base % i
            res = requests.get(url)
            doc = html.fromstring(res.content)
            for a in doc.findall('.//a'):
                article_url = urljoin(url, a.get('href', '/'))
                if 'allafrica.com/stories/' not in article_url:
                    continue
                try:
                    id = self.check_tag(url=article_url)
                    self.emit_url(url, packahe_id=id, article=True)
                except TagExists:
                    pass

        
