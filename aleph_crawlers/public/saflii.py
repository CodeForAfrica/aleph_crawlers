import logging
import requests
from urlparse import urljoin
from lxml import html

from aleph.crawlers import Crawler, TagExists

log = logging.getLogger(__name__)

INDEX = 'http://www.saflii.org/content/databases'


def is_year(el):
    text = el.text_content().strip()
    try:
        year = int(text)
        return year > 1900
    except ValueError:
        return False


class SafliiCrawler(Crawler):

    DEFAULT_LABEL = "SAFLII"
    DEFAULT_SITE = "http://www.saflii.org/"

    def crawl(self):
        res = requests.get(INDEX)
        doc = html.fromstring(res.content)
        for a in doc.findall('.//div[@class="node"]//a'):
            url = urljoin(INDEX, a.get('href'))
            self.crawl_database(url)

    def crawl_database(self, url):
        res = requests.get(url)
        doc = html.fromstring(res.content)
        # print 'DB URL', [res.url]
        links = set([urljoin(res.url, a.get('href'))
                     for a in doc.findall('.//a')])
        links.add(res.url)
        for a in doc.findall('.//a'):
            toc_url = urljoin(res.url, a.get('href'))
            if is_year(a):
                self.crawl_toc(toc_url, links)
            
    def crawl_toc(self, toc_url, links):
        res = requests.get(toc_url)
        doc = html.fromstring(res.content)
        for a in doc.findall('.//a'):
            doc_url = urljoin(res.url, a.get('href'))
            if doc_url in links:
                continue
            try:
                self.check_tag(url=doc_url)
                self.emit_url(doc_url, title=a.text_content().strip())
            except TagExists:
                pass
