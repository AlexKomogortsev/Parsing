# Task 1
from pprint import pprint
import requests
from urllib.parse import urlencode
from bs4 import BeautifulSoup as bs


def get_raw_data(url, headers, params, proxies):
    r = requests.get(url, headers=headers, params=params, proxies=proxies)
    return r


def save_raw_data(data, path):
    if data.status_code == 200:
        with open(path, 'w', encoding='UTF-8') as df:
            df.write(data.text)
    else:
        path = 'error'
    return path

# Сохранял отдельно в файл, чтобы не забанили
# save_raw_data(get_raw_data(url, headers=headers, params=vac1, proxies=proxies))


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
        min_salary = min_salary.replace(special, ' ')
    if max_salary is not None and special in max_salary:
        max_salary = max_salary.replace(special, ' ')

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


# Пропишем параметры для сайта
headers = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
}

proxies = {
    'http': 'http://83.97.108.99:8089'
}

url = "https://novosibirsk.hh.ru/search/vacancy/"

vac = input('Введите желаемую вакансию: ')
vac1 = urlencode({'text': vac})

# Получим html документ и линку с сайта
raw_data = get_raw_data(url, headers=headers, params=vac1, proxies=proxies)
soup = bs(raw_data.text, 'html.parser')

# Сохранял отдельно в файл, чтобы не забанили
# with open('hh_results.html', 'r', encoding='UTF-8') as file:
#     content = file.read()
#     soup = bs(content, 'lxml')

# Получим список вакансий
list_of_proposals = []

for i in soup.find_all(attrs={'class': 'vacancy-serp-item'}):
    list_of_proposals.append(get_proposal(i))

# Получим номер страницы
page_raw = soup.find('span', attrs={'data-qa': 'pager-page'})
if page_raw is not None:
    page_link = page_raw['to']
    page_num = page_raw['to'].split('=')[-1]
    page = int(page_num)

    last_page = soup.find_all('span', attrs={'class': 'pager-item-not-in-short-range'})

    # Получим список предложений
    pprint(list_of_proposals, sort_dicts=False)

    # Дадим возможность перейти на другую страницу
    input_page = input(
        f'\n Вы на странице # {page + 1} \n Всего страниц {last_page[-1].text} \n Какую выберете? Введите номер: ')

    page = int(input_page) - 1

    params = urlencode({
        'text': vac,
        'page': input_page
    })

    raw_data = get_raw_data(url, headers=headers, params=params, proxies=proxies)
    soup = bs(raw_data.text, 'html.parser')

    # Получим список вакансий
    list_of_proposals = []

    for i in soup.find_all(attrs={'class': 'vacancy-serp-item'}):
        list_of_proposals.append(get_proposal(i))

    pprint(list_of_proposals, sort_dicts=False)

else:
    print('Нет вакансий')
