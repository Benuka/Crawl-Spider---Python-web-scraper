
import os
import re
import codecs
import scrapy

from quotes.items import QuotesItem


class QuotespiderSpider(scrapy.Spider):
    #file extension which is going to save the results
    txt = '.txt'
    #indicate whole site or part of it 
    all = True
    #indicates the file name which is going to save the results
    fn = 'quotes.toscrape'
    #sites domain name
    dn = fn + '.com'

    #first page which will be scraped first
    firstPage = ['http://' + dn + '/page/1/']
    #scope for pages to crawl
    scope = [
        'http://' + dn + '/page/1/',
        'http://' + dn + '/page/2/',
        'http://' + dn + '/page/3/',
        'http://' + dn + '/page/4/',
    ]

    name = 'QuoteSpider'
    allowed_domains = [dn]
    start_urls = ['http://' + dn + '/page/1/']

#if the file already exsisits on the disk we need tor remove that
    def delFile(self):
        if os.path.exists(self.fn + self.txt):
            os.remove(self.fn + self.txt)

    def start_requests(self):
        self.delFile()
        pages = self.firstPage if self.all else self.scope
        
        for page in pages:
            yield scrapy.Request(page, self.parse)


    def extractData(self,res):
        q =  QuotesItem()

        for quote in res.css('div.quote'):
            q['quote'] = '"' + re.sub(r'[^\x00-\x7f]',r'', quote.css('span.text::text').extract_first()) + '"'
            q['author'] = quote.css('small.author::text').extract_first()
            q['tags'] = ' '.join(str(s) for s in quote.css('div.tags > a.tag::text').extract())

            self.writeTxt(q)

    def parse(self, response):
        self.extractData(response)

        if self.all:
            next = response.css('li.next > a::attr(href)').extract_first()
            if next is not None:
                yield scrapy.Request(response.urljoin(next))

    def writeTxt(self, q):
        with codecs.open(self.fn + self.txt, 'a+', 'utf-8') as f:
            f.write(q['quote'] + '\r\n')
            f.write(q['author'] + '\r\n')
            f.write(q['tags'] + '\r\n\n')
