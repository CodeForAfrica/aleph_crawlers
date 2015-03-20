import logging
import requests
from lxml import html
from urlparse import urljoin

from aleph.crawlers import Crawler, TagExists

log = logging.getLogger(__name__)


class AllAfricaCrawler(Crawler):

    LABEL = "AllAfrica"
    SITE = "http://allafrica.com/"

    def crawl(self):
        url_base = 'http://allafrica.com/latest/?page=%s'
        for i in xrange(1, 1000):
            url = url_base % i
            res = requests.get(url)
            doc = html.fromstring(res.content)
            for a in doc.findall('.//p[@class="title"]//a'):
                article_url = urljoin(url, a.get('href', '/'))
                if 'allafrica.com/stories/' not in article_url:
                    continue
                try:
                    id = self.check_tag(url=article_url)
                    title = a.text_content().strip()
                    self.emit_url(article_url, title=title,
                                  package_id=id, article=True)
                except TagExists:
                    pass

        
