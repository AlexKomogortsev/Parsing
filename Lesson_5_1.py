# Task 1

import time
from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import os
from dotenv import load_dotenv
from datetime import date, timedelta
import traceback


# Функция преобразования даты
def data_trans(date_row):
    data1 = date_row.split(',')[0]
    if data1 == 'Сегодня':
        data = date.today().strftime('%d/%B')
    elif data1 == 'Вчера':
        data = (date.today() - timedelta(days=1)).strftime('%d/%B')
    else:
        data = data1

    return data


# Функция, открывающая сайт
def open_page(link):
    driver = webdriver.Chrome(executable_path='./chromedriver.exe')
    driver.get(link)

    return driver


# Функция, открывающая список писем
def open_letters(driver, name, password):
    login_elem = driver.find_element_by_name('login')
    login_elem.send_keys(name)
    login_elem.send_keys(Keys.ENTER)

    pass_elem = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.NAME, 'password')))
    pass_elem.click()
    pass_elem.send_keys(password)
    pass_elem.send_keys(Keys.ENTER)

    return print('Страница писем открыта')


# Фукция, открывающая первое письмо
def open_first(driver):
    first_l = WebDriverWait(driver, 5).until(EC.element_to_be_clickable(
        (By.XPATH, '//a[@class="llc js-tooltip-direction_letter-bottom js-letter-list-item llc_normal"]')))
    first_l.click()

    return print('Первое письмо открыто')


# Функция получения информации из письма
def get_info(driver):
    info = {}

    try:
        letter_url = driver.current_url

        info['from'] = driver.find_element_by_xpath('//div[@class="letter__author"]/span').get_attribute('title')

        date_row = driver.find_element_by_xpath(
            '//div[@class="letter__author"]//div[@class="letter__date"]').text
        info['date'] = data_trans(date_row)
        info['theme'] = driver.find_element_by_xpath('//h2[@class="thread__subject"]').text
        info['text'] = driver.find_element_by_xpath('//div[@class="letter-body"]').text
    except Exception as e:
        print(f'ОШИБКА !!! {traceback.format_exc()}. Упали на письме по адресу: {letter_url}')

    return info


# Фунцкция, проходяшая по страницам писем и собирающая данные
def parsing(link, name, password):
    l = []

    driver = open_page(link)
    open_letters(driver, name, password)
    open_first(driver)
    time.sleep(0.7)
    next_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//span[@data-title-shortcut="Ctrl+↓"]')))

    while True:

        try:
            time.sleep(0.7)
            l.append(get_info(driver))
            next_button.click()
        except Exception as e:
            print(e)
            break

    print('Прошли все письма')

    return l


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
def update_mail_info(host, port, database, col, spisok, base_len):
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


# Заводим основные переменные
load_dotenv('.env')

name = os.getenv('name', None)
password = os.getenv('password', None)

link = 'https://mail.ru/'

# Пропишем пути к базе

MONGO_HOST = 'localhost'
MONGO_PORT = 27017
MONGO_DB = 'Messages'
MONGO_COLLECTION = 'mail_ru'

# Получим лист со всеми данными
print(
    f'{update_mail_info(MONGO_HOST, MONGO_PORT, MONGO_DB, MONGO_COLLECTION, parsing(link, name, password), get_col_len())} новых писем')
