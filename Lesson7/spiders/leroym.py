import scrapy
from scrapy.http import HtmlResponse
from leroy.items import LeroyItem
from scrapy.loader import ItemLoader


class LeroymSpider(scrapy.Spider):
    name = 'leroym'
    allowed_domains = ['leroymerlin.ru']

    def __init__(self, search):
        super(LeroymSpider, self).__init__()
        self.start_urls = [f'https://leroymerlin.ru/search/?q={search}&suggest=true']

    def parse(self, response: HtmlResponse):
        product_links = response.xpath('//div[@data-qa-product]/a/@href')
        next_page = response.xpath("//a[contains(@aria-label, 'Следующая')]").extract_first()

        for i in product_links:
            yield response.follow(i, callback=self.parse_good)

        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_good(self, response: HtmlResponse):
        loader = ItemLoader(item=LeroyItem(), response=response)
        loader.add_xpath('name', '//h1/text()')
        loader.add_xpath('photos', '//picture[@slot="pictures"]/source[contains(@media, "1024")]/@srcset')
        loader.add_xpath('price', '//meta[@itemprop="price"]/@content')
        loader.add_value('link', response.url)
        loader.add_xpath('char_types', '//section[@id="nav-characteristics"]//div[@class="def-list__group"]/dt/text()')
        loader.add_xpath('char_desc', '//section[@id="nav-characteristics"]//div[@class="def-list__group"]/dd/text()')

        # name = response.xpath('//h1/text()').extract_first()
        # photos = response.xpath(
        #     '//picture[@slot="pictures"]/source[contains(@media, "1024")]/@srcset').extract()
        # price = response.xpath('//meta[@itemprop="price"]/@content').extract_first()
        # link = response.url
        #
        # char_types = response.xpath(
        #     '//section[@id="nav-characteristics"]//div[@class="def-list__group"]/dt/text()').extract()
        # char_desc = response.xpath(
        #     '//section[@id="nav-characteristics"]//div[@class="def-list__group"]/dd/text()').extract()


        yield loader.load_item()
