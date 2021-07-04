# Task 3

from pprint import pprint
import requests
from urllib.parse import urlencode
from bs4 import BeautifulSoup as bs
from pymongo import MongoClient

# Параметры для подключения

headers = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
}

proxies = {
    'http': 'http://83.97.108.99:8089'
}

url = "https://novosibirsk.hh.ru/search/vacancy/"

# Обменный курс валют
change = {
    'KZT': 5.81,
    'руб.': 1,
    'EUR': 0.012,
    'USD': 0.014,
    'BLR': 0.035
}

# Параметры нашей БД
MONGO_HOST = 'localhost'
MONGO_PORT = 27017
MONGO_DB = 'head_hunter'
MONGO_COLLECTION = 'results'


# Функция получения страницы
def get_raw_data(url, headers, params, proxies):
    r = requests.get(url, headers=headers, params=params, proxies=proxies)
    return r


# Получение html по интересующей вакансии
def get_html():
    vac = input('Введите желаемую вакансию: ')
    vac1 = urlencode({'text': vac})

    raw_data = get_raw_data(url, headers=headers, params=vac1, proxies=proxies)
    soup = bs(raw_data.text, 'html.parser')

    return soup


# Функция получения зарплаты
def get_salary(salary_row):
    l = salary_row.split(' ')
    min_salary = None
    max_salary = None
    valuta = None

    # вытащим минимальные и максимальные значения зарплаты, если такие есть
    for i, j in enumerate(l):
        if j == 'от':
            min_salary = l[i + 1]
        elif j == '–':
            min_salary = l[i - 1]
            max_salary = l[i + 1]
        elif j == 'до':
            max_salary = l[i + 1]
        else:
            continue

    # обработаем unicode значения для пропусков в зарплате
    special = u'\u202f'

    if min_salary is not None and special in min_salary:
        min_salary = int(min_salary.replace(special, ''))
    if max_salary is not None and special in max_salary:
        max_salary = int(max_salary.replace(special, ''))

    # вытащим валюту
    if min_salary is not None or max_salary is not None:
        valuta = l[-1]

    # добавим все значения в словарь
    salary = {
        'min': min_salary,
        'max': max_salary,
        'currency': valuta
    }

    return salary


# Получение предложений по заданной вакансии
def get_proposal(vacancy):
    # вычленим элемент с названием вакансии и ссылкой на неё
    vac_anc = vacancy.find('a')
    vac_name = vac_anc.text

    vac_url = vac_anc['href']
    site = 'HeadHunter'

    # получим зарплату
    vac_salary_raw = vacancy.findChild('span', attrs={'data-qa': 'vacancy-serp__vacancy-compensation'})
    if vac_salary_raw is not None:
        vac_salary = vac_salary_raw.text
        salary = get_salary(vac_salary)
        min_salary = salary['min']
        max_salary = salary['max']
        valuta = salary['currency']
    else:
        min_salary = None
        max_salary = None
        valuta = None

    # Обернём все данные в словарь
    proposal = {
        'title': vac_name,
        'min': min_salary,
        'max': max_salary,
        'currency': valuta,
        'link': vac_url,
        'website': site
    }

    return proposal


# Функция получения списка вакансий
def get_list(soup):
    list_of_proposals = []

    for i in soup.find_all(attrs={'class': 'vacancy-serp-item'}):
        list_of_proposals.append(get_proposal(i))

    return list_of_proposals


# Функция записи данных в базу
def insert_vacs(host, port, database, col, spisok):
    with MongoClient(host, port) as client:
        db = client[database]
        collection = db[col]
        for i in spisok:
            collection.insert_one(i)

    return collection


# Функция получения объектов коллекции
def open_collection(host, port, database, col):
    with MongoClient(host, port) as client:
        db = client[database]
        collection = db[col]

    return collection.find({})


# Функция возвращает список вакансий, удовлетворяющих заданный уровень ЗП
def find_vacs(host, port, database, col):
    l = []
    query = int(input('Введите желаюмую зарплату в рублях: '))
    query_change = change
    for x, y in change.items():
        query_change[x] = y * query

    with MongoClient(host, port) as client:
        db = client[database]
        collection = db[col]

    cursor = collection.find({
        '$or': [
            {'$and': [
                {'max': {'$gt': query_change['KZT']}},
                {'currency': 'KZT'}]},
            {'$and': [
                {'max': {'$gt': query_change['руб.']}},
                {'currency': 'руб.'}]},
            {'$and': [
                {'max': {'$gt': query_change['EUR']}},
                {'currency': 'EUR'}]},
            {'$and': [
                {'max': {'$gt': query_change['USD']}},
                {'currency': 'USD'}]},
            {'$and': [
                {'max': {'$gt': query_change['BLR']}},
                {'currency': 'BLR'}]},
        ]
    })

    for doc in cursor:
        l.append(doc)

    return l


# Функция возвращает длину списка коллекции
def get_col_len():
    list = []
    for doc in open_collection(MONGO_HOST, MONGO_PORT, MONGO_DB, MONGO_COLLECTION):
        list.append(doc)
    length = len(list)

    return length


# Функция обновления списка новыми вакансиями. Возвращает количество новых значений
def update_vacs(host, port, database, col, spisok, base_len):
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


# Task 1. Первичное добавление вакансий в базу
insert_vacs(MONGO_HOST, MONGO_PORT, MONGO_DB, MONGO_COLLECTION, get_list(get_html()))

# Task 2. Ищем вакансии с нужной ЗП
pprint(find_vacs(MONGO_HOST, MONGO_PORT, MONGO_DB, MONGO_COLLECTION), sort_dicts=False)

# Task 3. Получаем количество обновленных вакансий
print(
    f'Список увеличился на {update_vacs(MONGO_HOST, MONGO_PORT, MONGO_DB, MONGO_COLLECTION, get_list(get_html()), get_col_len())} вакансии')
