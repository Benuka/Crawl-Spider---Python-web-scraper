# -*- coding: utf-8 -*-
import os
import re
import codecs
import scrapy

from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from quotes.items import QuotesItem


class QuotecrawlerSpider(CrawlSpider):
    #file extension which is going to save the results
    txt = '.txt'
    #indicates the file name which is going to save the results
    fn = 'quotes.toscrape'
    #sites domain name
    dn = fn + '.com'


    name = 'QuoteCrawler'
    allowed_domains = [dn]
    start_urls = ['http://' + dn +  '/page/1/']

    rules = (
        #different rules according to the need
        #Rule(LinkExtractor(allow=r'pag e/'), callback='parsepage', follow=True),
        #Rule(LinkExtractor(allow=r'tag/'), callback='parsepage', follow=True),
        #Rule(LinkExtractor(restrict_css='span.tag-item'), callback='parsepage', follow=True),
        Rule(LinkExtractor(restrict_css='li.next'), callback='parsepage', follow=True),
    )

    def extractData(self, res):
        q =  QuotesItem()

        for quote in res.css('div.quote'):
            q['quote'] = '"' + re.sub(r'[^\x00-\x7f]',r'', quote.css('span.text::text').extract_first()) + '"'
            q['author'] = quote.css('small.author::text').extract_first()
            q['tags'] = ' '.join(str(s) for s in quote.css('div.tags > a.tag::text').extract())

            self.writeTxt(q)

    def parsepage(self, response):
        self.extractData(response)

    def writeTxt(self, q):
        with codecs.open(self.fn +'1'+ self.txt, 'a+', 'utf-8') as f:
            f.write(q['quote'] + '\r\n')
            f.write(q['author'] + '\r\n')
            f.write(q['tags'] + '\r\n\n')