# Task 1

import requests
import json


def get_raw_data(url, params):
    r = requests.get(url, params=params)
    return r


def save_raw_data(data):
    if data.status_code == 200:
        path = 'dump_file.txt'
        with open(path, 'w') as df:
            df.write(data.text)
    else:
        path = 'error'
    return path


def get_repos(path, key):
    with open(path) as json_file:
        data = json.load(json_file)
    list = []
    for i in data:
        name = i[key]
        list.append(name)
    return list


def save_repos(list):
    path = 'repos_list.json'
    with open(path, 'w') as rl:
        json.dump(list, rl, indent=2)


u = 'https://api.github.com/users/AlexKomogortsev/repos'

p = {
    #    'accept': 'application/vnd.github.v3+json',
    'type': 'all'
}

where = save_raw_data(get_raw_data(u, p))

what = 'name'

repos_list = get_repos(where, what)

save_repos(repos_list)
