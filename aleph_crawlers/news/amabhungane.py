import logging
import requests
from itertools import count
from lxml import html

from aleph.crawlers import Crawler, TagExists

log = logging.getLogger(__name__)

INDEX = "http://amabhungane.co.za/archives/index/%s"


class AmaBhunganeCrawler(Crawler):

    DEFAULT_LABEL = "amaBhungane"
    DEFAULT_SITE = "http://amabhungane.co.za/"

    def crawl(self):
        for i in count(1):
            page_articles = set()
            url = INDEX % i
            res = requests.get(url)
            doc = html.fromstring(res.content)
            for a in doc.findall('.//a'):
                text = a.text_content().strip()
                url = a.get('href') or ''
                if '/article/' not in url or not len(text):
                    continue
                page_articles.add(url)
                try:
                    self.check_tag(url=url)
                    self.emit_url(url, title=text, article=True)
                except TagExists:
                    pass
            if not len(page_articles):
                return

        
