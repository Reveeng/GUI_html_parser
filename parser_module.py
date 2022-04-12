# -*- coding: utf-8 -*-
"""
Created on Tue Apr 12 11:47:53 2022

@author: egorn
"""

import requests
from bs4 import BeautifulSoup
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, QThread

import Utilities

'''Чтобы использовать создаем экземпляр класса, затем вызываем функцию parse_html(url)
где url ссылка на нужный нам сайт. В атрибуте last_repsonse будет лежать полученный html документ.
В атрибуте soup будет лежать объект BeautifulSoup
Чтобы получить статистику по тэгам html документа вызовите parser.get_all_tags()
'''

class ParseRunnable(QObject):
    finished = pyqtSignal('QVariant')
    def __init__(self,method, url, links):
        super().__init__()
        self.origin_url = url
        self.links = links
        self.method = method

    def set_tags(self,tags):
        self.all_tags = tags

    def run(self):
        for link in self.links:
            respContainer = Utilities.get_response(self.method+"//"+self.origin_url+link)
            if respContainer!= None:
                new_tags = [tag.name for tag in respContainer.soup.find_all()]
                self.all_tags = [*self.all_tags, *new_tags]
        self.finished.emit(self.all_tags)


class Parser(QObject):
    finished = pyqtSignal()

    def __init__(self, parent = None):
        return super().__init__(parent)

    @pyqtSlot(str, result = 'QVariant')
    def parse_html(self, url):
        respContainer = Utilities.get_response(url)
        if (respContainer  != None):
            self.last_repsonse = respContainer.response
            self.soup = respContainer.soup
            split_url = url.split('/')
            for token in split_url:
                if '.' in token:
                    self.origin_url = token
                    break
            self.method = split_url[0]
            return True
        else:
            return False

    def on_parse_finished(self, all_tags):
        self.tag_dict = Utilities.get_tags_count(all_tags)
        self.finished.emit()

    @pyqtSlot(result = 'QVariant')
    def get_stat(self):
        return self.tag_dict

    @pyqtSlot()
    def get_tags_stats(self):
        links = [link.get('href') for link in  self.soup.find_all('a')]
        all_tags = [tag.name for tag in self.soup.find_all()]
        origin_links = Utilities.get_valid_links(links, self.origin_url)
        self.runnable = ParseRunnable(self.method,self.origin_url,origin_links)
        self.runnable.set_tags(all_tags)
        self.thread  = QThread()
        self.runnable.moveToThread(self.thread)
        self.runnable.finished.connect(self.on_parse_finished)
        self.thread.started.connect(self.runnable.run)
        self.runnable.finished.connect(self.thread.quit)
        self.runnable.finished.connect(self.thread.deleteLater)
        self.runnable.finished.connect(self.runnable.deleteLater)
        self.thread.start()

    @pyqtSlot()
    def get_all_images(self):
        images = self.soup.find_all(['svg', 'img'])



