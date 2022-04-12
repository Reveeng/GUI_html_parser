# -*- coding: utf-8 -*-
"""
Created on Tue Apr 12 11:47:53 2022

@author: egorn
"""

import requests
from bs4 import BeautifulSoup
import numpy as np
from multiprocessing.dummy import Pool
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, QThread

'''Чтобы использовать создаем экземпляр класса, затем вызываем функцию parse_html(url)
где url ссылка на нужный нам сайт. В атрибуте last_repsonse будет лежать полученный html документ.
В атрибуте soup будет лежать объект BeautifulSoup
Чтобы получить статистику по тэгам html документа вызовите parser.get_all_tags()
'''

class ParseRunnable(QObject):
    finished = pyqtSignal('QVariant')
    def __init__(self, header, url, links):
        super().__init__()
        self.header = header
        self.origin_url = url
        self.links = links

    def set_tags(self,tags):
        self.all_tags = tags

    def run(self):
        for link in self.links:
            resp = requests.get(self.origin_url+link, headers = self.header).text
            soup = BeautifulSoup(resp,'lxml')
            new_tags = [tag.name for tag in soup.find_all()]
            self.all_tags = [*self.all_tags, *new_tags]
        self.finished.emit(self.all_tags)


class Parser(QObject):
    finished = pyqtSignal()

    def __init__(self, parent = None):
        self.header = {'User-Agent':
                       'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'}
        self.num_threads = 2
        return super().__init__(parent)

    @pyqtSlot(str, result = 'QVariant')
    def parse_html(self, url):
        try:
            resp = requests.get(url,headers = self.header)
            self.last_response = resp.text
            self.soup = BeautifulSoup(self.last_response, 'lxml')
        except:
            return False
        else:
            self.origin_url = url
            return True

    def clear_links(self, links):
        clear_links =  []
        for link in links:
            if (link != None):
                if link.startswith('/') and len(link) > 1:
                    clear_links.append(link)
        return clear_links

    def get_tag_dict(self, tags):
        unique_tags = []
        if (len(tags) > 10000):
            unique_tags = np.unique(np.concatenate(
                    Pool(self.n_threads).map(np.unique, np.array_split(tags, self.n_threads)))).tolist()
        else:
            unique_tags = list(set(tags))
        tag_dict = {}
        for tag in unique_tags:
            tag_dict[tag] = tags.count(tag)
        return tag_dict

    def test(self, all_tags):
        self.tag_dict = self.get_tag_dict(all_tags)
        self.finished.emit()

    @pyqtSlot(result = 'QVariant')
    def get_stat(self):
        return self.tag_dict

    @pyqtSlot(result = 'QVariant')
    def get_tags_stats_recursive(self):
        links = [link.get('href') for link in  self.soup.find_all('a')]
        all_tags = [tag.name for tag in self.soup.find_all()]
        self.origin_links = self.clear_links(links)
        self.runnable = ParseRunnable(self.header, self.origin_url,self.origin_links)
        self.runnable.set_tags(all_tags)
        self.thread  = QThread()
        self.runnable.moveToThread(self.thread)
        self.runnable.finished.connect(self.test)
        self.thread.started.connect(self.runnable.run)
        self.runnable.finished.connect(self.thread.quit)
        self.runnable.finished.connect(self.thread.deleteLater)
        self.runnable.finished.connect(self.runnable.deleteLater)
        self.thread.start()
#        return self.get_tag_dict(all_tags)



        
    @pyqtSlot(result = 'QVariant')
    def get_tags_stats(self):
        all_tags = [tag.name for tag in self.soup.find_all()]
        return self.get_tag_dict(all_tags)

    @pyqtSlot()
    def get_all_images(self):
        images = self.soup.find_all(['svg', 'img'])



