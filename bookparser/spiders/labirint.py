import scrapy
from scrapy.http import HtmlResponse
from bookparser.items import BookparserItem


class LabirintSpider(scrapy.Spider):
    name = 'labirint'
    allowed_domains = ['labirint.ru']
    start_urls = [
        'https://www.labirint.ru/search/%D0%9D%D0%9B%D0%9E/?stype=0']

    def parse(self, response: HtmlResponse):
        book_links = response.xpath('//div[@class="product-cover__cover-wrapper"]/a/@href').extract()
        next_page = response.xpath('//a[@title="Следующая"]/@href').extract_first()
        for link in book_links:
            yield response.follow(link, callback=self.get_bookinfo)

        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def get_bookinfo(self, response: HtmlResponse):
        link = response.url
        title = response.xpath('//div[@id="product-title"]/h1/text()').extract_first()
        author = response.xpath('//a[@data-event-label="author"]/text()').extract_first()
        price_init = response.xpath('//span[@class="buying-priceold-val-number"]/text() | //span[@class="buying-price-val-number"]/text()').extract_first()
        price_new = response.xpath('//span[@class="buying-pricenew-val-number"]/text() | //span[@class="buying-price-val-number"]/text()').extract_first()
        rating = response.xpath('//div[@id="rate"]/text()').extract_first()

        item = BookparserItem(link=link, title=title, author=author, price_init=price_init, price_new=price_new,
                              rating=rating)

        yield item
