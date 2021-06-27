# Task 2
import requests
import os
from dotenv import load_dotenv

load_dotenv('.env')

api = os.getenv('APIkey', None)


def get_weather(url, params):
    weather = requests.get(url, params=params)
    temp = weather.json()["main"]
    temp_now = temp['temp']
    return temp_now


url = 'https://api.openweathermap.org/data/2.5/weather'
city = input('Введите название города: ')
p = {
    'appid': api,
    'q': city,
    'units': 'metric',
    'lang': 'ru'
}

print(f'Температура в городе {city} равна {get_weather(url, p)} градусов цельсий')
