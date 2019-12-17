# -*- coding: utf-8 -*-
import scrapy


class DetikNewsSpider(scrapy.Spider):
    name = "detiknews"
    allowed_domain = ["news.detik.com",]
    start_urls = [
        "https://news.detik.com/indeks",
    ]

    def parse(self, response):
        for article_url in response.css(".media__title  > a::attr(href)").extract():
            yield scrapy.Request(
                response.urljoin("{}?single=1".format(article_url)),
                callback=self.parse_article_page,
            )

        next_link = response.css(".pagination > a")[-1]
        next_page = next_link.css("::attr(href)").extract_first()

        if (next_page):
            yield scrapy.Request(response.urljoin(next_page), callback=self.parse)

    def parse_article_page(self, response):
        item = {
            "source": "detiknews",
            "type": "article",
            "slug": response.request.url,
        }

        # Get category
        breadcrumb_link = response.css(".page__breadcrumb > a")[-1]
        item["category"] = breadcrumb_link.css("::text").extract_first()

        data = response.css("article.detail")
        header = data.css(".detail__header")
        media = data.css(".detail__media")
        content = data.css(".detail__body-text")
        tags = data.css(".detail__body-tag")

        # Get title
        title = header.css("h1.detail__title::text").extract_first()
        item["title"] = None
        if title:
            item["title"] = title.replace("\n         ", "").replace("    ", "").replace("\n", "")

        # Get author
        author = header.css(".detail__author::text").extract_first()
        item["author"] = None
        if author:
            item["author"] = author.replace(" - detikNews", "")

        # Get date (String)
        item["date"] = header.css(".detail__date::text").extract_first()

        # Get media url
        item["media"] = media.css("figure.detail__media-image > img::attr(src)").extract()

        # Get tags
        item["tags"] = tags.css(".nav > a::text").extract()

        # Get raw content
        content = data.css(".detail__body-text")
        item["contentRaw"] = content.get()



        yield item
