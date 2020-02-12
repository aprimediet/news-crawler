# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime


class KompasNewsSpider(scrapy.Spider):
    name = "kompasnews"
    allowed_domain = ["news.kompas.com",]
    # start_urls = [
    #     "https://news.detik.com/indeks",
    # ]
    base_url = "https://news.kompas.com/search"

    def __init__(self, start_date=None, end_date=None, *args, **kwargs):
        super(KompasNewsSpider, self).__init__(*args, **kwargs)

        self.start_date = None
        self.end_date = None

        if (start_date != None and end_date != None):
            _start_part = start_date.split('-')
            _end_part = end_date.split('-')

            _start_year = int(_start_part[0])
            _start_month = int(_start_part[1])
            _start_date = int(_start_part[2])

            _end_year = int(_end_part[0])
            _end_month = int(_end_part[1])
            _end_date = int(_end_part[2])

            if _end_date < _start_date:
                raise scrapy.exceptions.CloseSpider(reason="Start date must be lower than end date")

            if _start_year != _end_year:
                raise scrapy.exceptions.CloseSpider(reason="Cannot crawl within different year range")

            if _start_month != _end_month:
                raise scrapy.exceptions.CloseSpider(reason="Cannot crawl within different month range")

            self.start_date = datetime.strptime(start_date, "%Y-%m-%d")
            self.end_date = datetime.strptime(end_date, "%Y-%m-%d")

    def start_requests(self):
        _ranged = [
            self.base_url,
        ]

        if (self.start_date != None and self.end_date != None):
            _ranged = []
            
            start_range = self.start_date.day
            end_range = self.end_date.day + 1

            for date in range(start_range, end_range):
                _ranged.append(
                    "{}/{}-{:02d}-{:02d}".format(
                        self.base_url,
                        self.start_date.year,
                        self.start_date.month,
                        date,
                    )
                )

        for url in _ranged:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        for article_url in response.css(".article__title  > a::attr(href)").extract():
            yield scrapy.Request(
                response.urljoin("{}?page=all".format(article_url)),
                callback=self.parse_article_page,
            )

        next_page = response.css("a.paging__link--next::attr(href)").extract_first()

        if (next_page):
            yield scrapy.Request(response.urljoin(next_page), callback=self.parse)

    def parse_article_page(self, response):
        item = {
            "source": "kompasnews",
            "type": "article",
            "slug": response.request.url,
        }

        # Get category
        breadcrumb_link = response.css("li.breadcrumb__item > a")[-1]
        item["category"] = breadcrumb_link.css("span::text").extract_first()

        # data = response.css("article.detail")
        # header = data.css(".detail__header")
        # media = data.css(".detail__media")
        # content = data.css(".detail__body-text")
        # tags = data.css(".detail__body-tag")

        # Get title
        title = response.css("h1.read__title::text").extract_first()
        # item["title"] = None
        # if title:
        #     item["title"] = title.replace("\n         ", "").replace("    ", "").replace("\n", "")

        # Get author
        author = response.css("div#editor > a::text").extract_first()
        # item["author"] = None
        # if author:
        #     item["author"] = author.replace(" - KompasNews", "")

        # Get date (String)
        date = response.css(".read__time::text").extract_first()
        item["date"] = None
        if date:
            item["date"] = date.replace("Kompas.com - ", "")

        # Get media url
        item["media"] = response.css("div.photo > div.photo__wrap > img::attr(src)").extract()

        # Get tags
        item["tags"] = response.css("li.tag__article__item > a::text").extract()

        # Get raw content
        content = response.css("div.read__content > p::text")
        item["contentRaw"] = content.extract()

        item["createdAt"] = datetime.now()

        yield item
