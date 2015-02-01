import logging
import requests
from itertools import count
from lxml import html
from urlparse import urljoin

from aleph.crawlers import Crawler, TagExists

log = logging.getLogger(__name__)

BASES = [('http://africacheck.org/how-to-fact-check/factsheets-and-guides/page/%d/', '/factsheets/'),
         ('http://africacheck.org/latest-reports/page/%d/', '/reports/')]


class AfricaCheckCrawler(Crawler):

    DEFAULT_LABEL = "AfricaCheck"
    DEFAULT_SITE = "http://africacheck.org/"

    def crawl(self):
        for (base_url, urlfrag) in BASES:
            self.crawl_section(base_url, urlfrag)

    def crawl_section(self, base_url, urlfrag):
        for i in count(1):
            page_urls = set()
            url = base_url % i
            res = requests.get(url)
            doc = html.fromstring(res.content)
            for a in doc.findall('.//article//a'):
                article_url = urljoin(url, a.get('href', '/'))
                title = a.text_content().strip()
                if urlfrag not in article_url:
                    continue

                if not len(title) or 'comment' in a.get('class', ''):
                    continue
                page_urls.add(article_url)
                try:
                    id = self.check_tag(url=article_url)
                    self.emit_url(article_url, title=title,
                                  package_id=id, article=True)
                except TagExists:
                    pass
            if not len(page_urls):
                return


        
