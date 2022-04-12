# This Python file uses the following encoding: utf-8

from multiprocessing.dummy import Pool
import numpy as np
import requests
from bs4 import BeautifulSoup

header = {'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'}

class ResponceContainer():
    def __init__(self, response,soup):
        self.response = response
        self.soup = soup



def get_unique_array(array, num_threads = 2):
    unique_tags = []
    if (len(array) > 10000):
        unique_tags = np.unique(np.concatenate(
                Pool(num_threads).map(np.unique, np.array_split(array, num_threads)))).tolist()
    else:
        unique_tags = list(set(array))

    return unique_tags

def get_valid_links(links, support_url):
    clear_links = []
    for link in links:
        if link != None:
            if link.startswith('/') and len(link) > 1:
                clear_links.append(link)
            elif link.startswith(support_url):
                clear_links.append(link)
    return clear_links

def get_response(url):
    resContainer = None
    try:
        resp = requests.get(url, headers = header).text
        resContainer = ResponceContainer(resp, BeautifulSoup(resp, 'lxml'))
    except:
        return None
    else:
        return resContainer

def get_tags_count(tags):
    unique_tags = get_unique_array(tags)
    tag_dict = {}
    for tag in unique_tags:
        tag_dict[tag] = tags.count(tag)
    return tag_dict
