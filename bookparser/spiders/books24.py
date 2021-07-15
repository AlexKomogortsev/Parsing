import scrapy
from scrapy.http import HtmlResponse
from bookparser.items import BookparserItem


class Books24Spider(scrapy.Spider):
    name = 'books24'
    allowed_domains = ['book24.ru']
    start_urls = ['https://book24.ru/search/?q=%D0%9D%D0%9B%D0%9E']

    def parse(self, response: HtmlResponse):
        book_links = response.xpath('//a[@class="product-card__image-link smartLink"]/@href').extract()
        next_page = response.xpath('//a[@class="pagination__item _link _button _next smartLink"]/@href').extract_first()
        for link in book_links:
            yield response.follow(link, callback=self.get_bookinfo)

        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def get_bookinfo(self, response: HtmlResponse):
        link = response.url
        title = response.xpath('//h1[@class="product-detail-page__title"]/text()').extract()
        author = response.xpath('//span[contains(.,"Автор")]/../..//a/text()').extract()
        price_init = response.xpath(
            '//span[@class="app-price product-sidebar-price__price-old"]/text() | //span[@class="app-price product-sidebar-price__price"]/text()').extract_first()
        price_new = response.xpath(
            '//span[@class="app-price product-sidebar-price__price"]/text() | //span[@class="app-price product-sidebar-price__price"]/text()').extract_first()
        rating = response.xpath('//span[@class="rating-widget__main-text"]/text()').extract_first()

        item = BookparserItem(link=link, title=title, author=author, price_init=price_init, price_new=price_new,
                              rating=rating)

        yield item
