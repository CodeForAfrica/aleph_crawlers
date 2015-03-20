import logging
import requests
from urlparse import urljoin
from lxml import html

from aleph.crawlers import Crawler, TagExists
from aleph_crawlers.util import clean


log = logging.getLogger(__name__)

BASE = 'http://documents.worldbank.org/curated/en'
TYPE_LIST = BASE + '/document-type'
TYPE_URL = BASE + '/docsearch/document-type/%s'
INDEX_PAGE = 50
INDEX_URL = BASE + '/documentsearchpagination'
INDEX_ARGS = {
    'pageView': 'detail',
    'noOfRows': INDEX_PAGE,
    'startIndex': '0',
    'lang': 'en',
    'clickIndex': '2',
    'activeStartIndex': '0',
    'activeEndIndex': '10',
    'paramKey': 'srt',
    'paramValue': 'docdt',
    'sortOrder': 'desc',
    'facetSessionTerm': 'docType',
    'sessionQueryTerm': '~~~docty_key=563774',
    'strdate': '',
    'enddate': '',
    'tf': '',
    'lType': '',
}


class WorldBankDocsCrawler(Crawler):

    LABEL = "WorldBank Documents"
    SITE = "http://documents.worldbank.org/"

    def crawl_type_list(self):
        res = requests.get(TYPE_LIST)
        doc = html.fromstring(res.content)
        for a in doc.findall('.//div[@class="browsecontent"]//a'):
            if '/docsearch/' not in a.get('href'):
                continue
            yield urljoin(TYPE_LIST, a.get('href'))

    def crawl_document_type(self, url):
        session = requests.Session()
        res = session.get(url)
        urls = set()
        for offset in range(0, 10000000, INDEX_PAGE):
            args = INDEX_ARGS.copy()
            args['startIndex'] = offset
            res = session.post(INDEX_URL, data=args)
            doc = html.fromstring(res.content)
            before_count = len(urls)
            for link in doc.findall('.//td/a'):
                href = link.get('href')
                if not href.lower().startswith('http:'):
                    continue
                urls.add(urljoin(INDEX_URL, link.get('href')))
                self.crawl_document(urljoin(INDEX_URL, href))
            if len(urls) == before_count:
                break

    def crawl_document(self, url):
        try:
            self.check_tag(url=url)
        except TagExists:
            pass

        res = requests.get(url)
        doc = html.fromstring(res.content)
        data = {
            'details_url': url,
            'title': doc.findtext('.//div[@class="c00v3-introduction"]/h1'),
            'summary': doc.findtext('.//span[@id="detail_abstract"]') or
            doc.findtext('.//span[@id="summary_abstract"]')
        }

        log.info("Crawling WB document: %s, %s", data['title'], url)

        if doc.find('.//div[@id="CitationHidDiv"]') is not None:
            text = clean(doc.find('.//div[@id="CitationHidDiv"]'))
            data['citation'] = text

        for li in doc.findall('.//ul[@class="detail"]/li'):
            label = li.findtext('./label')
            if label is None:
                continue
            label = label.replace('.', '').replace('/', '')
            label = label.replace(' ', '_').lower()
            value = li.find('./span').xpath('string()')
            label = label.replace('(s)', '')
            data[label] = clean(value)

        for li in doc.findall('.//ul[@class="documentLnks"]/li'):
            record = data.copy()
            if li.get('class') != 'textdoc':
                doc_url = li.find('a').get('href')
                self.emit_url(doc_url, title=data['title'],
                              summary=data['summary'],
                              meta=record)
     
    def crawl(self):
        doc_type = self.source.config.get('document_type')
        if doc_type is not None:
            url = TYPE_URL % doc_type
            self.crawl_document_type(url)
        else:
            for url in self.crawl_type_list():
                self.crawl_document_type(url)
