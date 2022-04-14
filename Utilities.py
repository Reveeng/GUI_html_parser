# This Python file uses the following encoding: utf-8

from multiprocessing.dummy import Pool
import numpy as np
import requests
from bs4 import BeautifulSoup

#Заголовок для запросов
header = {'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'}

#Класс контейнера, содержит все, что мне нужно, после получения ответа от сервера на котором расположен сайт
#То есть текстовый ответ response и soup версию разметки
class ResponceContainer():
    def __init__(self, response,soup):
        self.response = response
        self.soup = soup


#Принимает на вход массив каких-то данных и колличество потоков. По умолчанию потока 2
#Возвращает массив уникальных объектов из переданного массива
def get_unique_array(array, num_threads = 2):
    unique_tags = []
#    Если длинна масива больше 100000 обработка производится с помощью numpy array и в несколько потоков
#    Если меньше то это не имеет особого смысла
    if (len(array) > 10000):
        unique_tags = np.unique(np.concatenate(
                Pool(num_threads).map(np.unique, np.array_split(array, num_threads)))).tolist()
    else:
        unique_tags = list(set(array))

    return unique_tags

#Принимает массив ссылок возвращает валидные ссылки (это ссылки которые начинатся с / либо с url сайта)
#Ссылки на другие ресурсы отбрасываются
def get_valid_links(links, support_url):
    clear_links = []
    for link in links:
        if link != None:
            if link.startswith('/') and len(link) > 1:
                clear_links.append(link)
            elif link.startswith(support_url):
                clear_links.append(link)
    return clear_links

#Отправляет запрос на сервер. Если произошла ошибка возвращает None, если все нормально, то возвращает контейнер
def get_response(url):
    resContainer = None
    try:
        resp = requests.get(url, headers = header).text
        resContainer = ResponceContainer(resp, BeautifulSoup(resp, 'lxml'))
    except:
        return None
    else:
        return resContainer

#Принимет на вход массив тегов которые вообще есть на сайте. Возвращает словарь вида Tag - count
def get_tags_count(tags):
    unique_tags = get_unique_array(tags)
    tag_dict = {}
    for tag in unique_tags:
        tag_dict[tag] = tags.count(tag)
    return tag_dict
