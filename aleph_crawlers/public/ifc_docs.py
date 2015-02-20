import logging
import requests
from itertools import count
from urlparse import urljoin
from lxml import html

from aleph.crawlers import Crawler, TagExists
from aleph_crawlers.util import clean


log = logging.getLogger(__name__)

PAGE_SIZE = 100
INDEX = 'http://ifcext.ifc.org/ifcext/spiwebsite1.nsf/frmshowview?openform&view=CRUDate&start=%s&count=%s&page=%s'


class IFCDocsCrawler(Crawler):

    DEFAULT_LABEL = "IFC Documents"
    DEFAULT_SITE = "http://ifcextapps.ifc.org/ifcext/spiwebsite1.nsf/$$Search?openform"

    def crawl(self):
        urls = set()
        for i in count(1):
            offset = ((i - 1) * PAGE_SIZE) + 1
            url = INDEX % (offset, PAGE_SIZE, i)
            res = requests.get(url)
            doc = html.fromstring(res.content)
            before_count = len(urls)
            for link in doc.findall('.//tr/td//a'):
                purl = urljoin(url, link.get('href'))
                urls.add(purl)
                self.crawl_document(purl)
            if len(urls) == before_count:
                break

    def crawl_document(self, url):
        try:
            id = self.check_tag(url=url)

            res = requests.get(url)
            doc = html.fromstring(res.content)
            data = {
                'url': url,
                'title': doc.findtext('.//td[@class="pageHeading"]'),
                'report': doc.findtext('.//td[@class="pageSubHeading"]')
            }
            for row in doc.findall('.//tr'):
                label = row.find('./td[@class="labelCell"]')
                if label is None or label.text is None:
                    continue
                label = clean(label.text)
                label = label.replace('.', '').replace('/', '').replace(' ', '_').lower()
                label = label.replace('sector1', 'sector')
                node = row.find('./td[@class="dataCell"]')
                if node is not None:
                    value = clean(node.xpath('string()'))
                    data[label] = value

            self.emit_url(url, package_id=id, mime_type='text/html',
                          extension='html', article=True, meta=data)

            attachments = doc.find('.//input[@name="AttachmentNames"]')
            if attachments is not None:
                # GOT TO BE FUCKING KIDDING ME
                attachments = attachments.get('value').split('^~')
                docid = doc.find('.//input[@name="DocID"]').get('value')
                for attachment in attachments:
                    if not len(attachment.strip()):
                        continue
                    aurl = 'http://ifcext.ifc.org/ifcext/spiwebsite1.nsf/0/%s/$File/%s'
                    aurl = aurl % (docid, attachment)
                    try:
                        aid = self.check_tag(url=aurl)
                        print "AURL", aurl
                        self.emit_url(aurl, package_id=aid,
                                      meta=data)
                    except TagExists:
                        pass
        except TagExists:
            pass
