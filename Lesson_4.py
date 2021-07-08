# Lesson 4

import requests
from lxml.html import fromstring
from datetime import timedelta, date
from pymongo import MongoClient


# Функция получения дерева html
def get_dom(url, headers, proxies):
    response = requests.get(url, headers=headers, proxies=proxies)
    dom = fromstring(response.text)

    return dom


# Парсинг Ленты
def get_lenta_params(items_xpath, url, headers, proxies):
    dom = get_dom(url, headers=headers, proxies=proxies)
    items = dom.xpath(items_xpath)
    info_about_items = []

    for i in items:
        info = {}
        info['source'] = 'Lenta'

        if len(i.xpath('./a/text()')) > 0:
            info['title'] = i.xpath('./a/text()')[0]
        else:
            info['title'] = None

        if len(i.xpath('./a/@href')) > 0:
            info['link'] = url + i.xpath('./a/@href')[0]
        else:
            info['link'] = None

        if len(i.xpath('./a/time/@title')) > 0:
            info['date'] = i.xpath('./a/time/@title')[0]
        else:
            info['date'] = None

        info_about_items.append(info)

    return info_about_items


# Парсинг Яндекса
def get_yandex_params(items_xpath, url, headers, proxies):
    dom = get_dom(url, headers=headers, proxies=proxies)
    items = dom.xpath(items_xpath)
    info_about_items = []

    for i in items:
        info = {}

        if len(i.xpath('.//div[@class="mg-card-footer mg-card__footer mg-card__footer_type_image"]//'
                       'span[@class="mg-card-source__source"]/a/@aria-label')) > 0:
            info['source'] = i.xpath('.//div[@class="mg-card-footer mg-card__footer mg-card__footer_type_image"]//'
                                     'span[@class="mg-card-source__source"]/a/@aria-label')[0]
        else:
            info['source'] = None

        if len(i.xpath('.//div[@class="mg-card__inner"]/a/h2/text() | '
                       './/div[@class="mg-card__text-content"]//a/h2/text()')) > 0:
            info['title'] = i.xpath('.//div[@class="mg-card__inner"]/a/h2/text() | '
                                    './/div[@class="mg-card__text-content"]//a/h2/text()')[0].replace(
                '&nbsp;', ' ').replace('\xa0', ' ')
        else:
            info['title'] = None

        if len(i.xpath(
                './/div[@class="mg-card__inner"]/a/@href | .//div[@class="mg-card__text-content"]//a/@href')) > 0:
            info['link'] = i.xpath('.//div[@class="mg-card__inner"]/a/@href |'
                                   ' .//div[@class="mg-card__text-content"]//a/@href')[0]
        else:
            info['link'] = None

        data = i.xpath('.//div[@class="mg-card-footer mg-card__footer mg-card__footer_type_image"]//'
                       'span[@class="mg-card-source__time"]/text()')
        if len(data) > 0:
            data_str = data[0].split(' ')
            if data_str[0] == 'вчера':
                info['date'] = (date.today() - timedelta(days=1)).strftime('%d/%m/%y')
            else:
                info['date'] = date.today().strftime('%d/%m/%y')
        else:
            info['date'] = None

        info_about_items.append(info)

    return info_about_items


# Парсинг Мэйла
def get_mail_params(items_xpath, url, headers, proxies):
    dom = get_dom(url, headers=headers, proxies=proxies)
    items = dom.xpath(items_xpath)
    info_about_items = []

    for i in items:
        link = i.xpath('.//a/@href')[0]
        dom1 = get_dom(link, headers=headers, proxies=proxies)
        m_items_xpath1 = '//div[@class="cols__wrapper"]'
        items1 = dom1.xpath(m_items_xpath1)

        info = {}

        for item in items1:
            if len(item.xpath('.//span[@class="note"]/a/span/text()')) > 0:
                info['source'] = item.xpath('.//span[@class="note"]/a/span/text()')[0]
            else:
                break

            if len(item.xpath('.//span[@class="hdr__text"]/h1/text()')) > 0:
                info['title'] = item.xpath('.//span[@class="hdr__text"]/h1/text()')[0]
            else:
                info['title'] = None

            info['link'] = link

            data = item.xpath('.//span[@class="note__text breadcrumbs__text js-ago"]/text()')
            if len(data) > 0:
                data_str = data[0].split(' ')
                if data_str[0] == 'вчера':
                    info['date'] = (date.today() - timedelta(days=1)).strftime('%d/%m/%y')
                else:
                    info['date'] = date.today().strftime('%d/%m/%y')
            else:
                info['date'] = None

            info_about_items.append(info)

    return info_about_items


# Функция получения объектов коллекции
def open_collection(host, port, database, col):
    with MongoClient(host, port) as client:
        db = client[database]
        collection = db[col]

    return collection.find({})


# Функция возвращает длину списка коллекции
def get_col_len():
    list = []
    for doc in open_collection(MONGO_HOST, MONGO_PORT, MONGO_DB, MONGO_COLLECTION):
        list.append(doc)
    length = len(list)

    return length


# Функция обновления новостей в базе
def update_news(host, port, database, col, spisok, base_len):
    with MongoClient(host, port) as client:
        db = client[database]
        collection = db[col]

        for i, j in enumerate(spisok):
            filter_data = j
            update_data = {
                '$set': j
            }
            collection.update_one(filter_data, update_data, upsert=True)
    new_len = get_col_len()
    diff = new_len - base_len

    return diff


# lenta.ru

proxies = {
    'http': 'http://83.97.108.99:8089'
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                  ' AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

l_url = 'https://lenta.ru/'

l_items_xpath = '//section[contains(@class, "row b-top7-for-main js-top-seven")]' \
                '/div[contains(@class, "span4")]/div[contains(@class, "item")]'

# yandex.ru

y_url = 'https://yandex.ru/news/'

y_items_xpath = '//div[contains(@class, ' \
                '"mg-grid__row mg-grid__row_gap_8 news-top-flexible-stories news-app__top")]/div'

# mail.ru

m_url = 'https://news.mail.ru/'

m_items_xpath = '//div[@class="daynews__item"] | //div[@class="daynews__item daynews__item_big"]'

# Положим всё в базу

MONGO_HOST = 'localhost'
MONGO_PORT = 27017
MONGO_DB = 'News'
MONGO_COLLECTION = 'News'

# Добавим новости с Ленты
print(
    f'{update_news(MONGO_HOST, MONGO_PORT, MONGO_DB, MONGO_COLLECTION, get_lenta_params(l_items_xpath, l_url, headers, proxies), get_col_len())} новых новостей')

# Продублируем, чтобы проверить добавляются ли старые записи
print(
    f'{update_news(MONGO_HOST, MONGO_PORT, MONGO_DB, MONGO_COLLECTION, get_lenta_params(l_items_xpath, l_url, headers, proxies), get_col_len())} новых новостей')

# Добавим новости с Яндекса
print(
    f'{update_news(MONGO_HOST, MONGO_PORT, MONGO_DB, MONGO_COLLECTION, get_yandex_params(y_items_xpath, y_url, headers, proxies), get_col_len())} новых новостей')

# Добавим новости с Мэйла
print(
    f'{update_news(MONGO_HOST, MONGO_PORT, MONGO_DB, MONGO_COLLECTION, get_mail_params(m_items_xpath, m_url, headers, proxies), get_col_len())} новых новостей')
