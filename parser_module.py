# -*- coding: utf-8 -*-
"""
Created on Tue Apr 12 11:47:53 2022

@author: egorn
"""
#Импортирую библиотеки для работы с сетью
import requests
from bs4 import BeautifulSoup
#Импортирую класс QObject, от него должен быть унаследован любой класс который я хочу передать в контекст движка
#QThread это обертка над C++ классом работы с потоками. Не знаю как оно работает в питоне, но в ++ создается отдельный поток выполнения какой-то функции
#Это нужно, чтобы при выполнении парсинга GUI не зависало
#О сигналах и слотах долго писать
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, QThread

#Импортирую файл с вспомогательными функциями по работе с массивами
import Utilities
import os

'''Чтобы использовать создаем экземпляр класса, затем вызываем функцию parse_html(url)
где url ссылка на нужный нам сайт. В атрибуте last_repsonse будет лежать полученный html документ.
В атрибуте soup будет лежать объект BeautifulSoup
Чтобы получить статистику по тэгам html документа вызовите parser.get_all_tags()
'''



class DrawRunnable(QObject):
    finished = pyqtSignal()

    def __init__(self, nodes, edges, parent = None):
        super().__init__(parent)
        self.nodes = nodes
        self.edges = edges

    def run(self):
        Utilities.draw_graph(self.nodes, self.edges)
        self.finished.emit()

class DownloadRunnable(QObject):
    finished = pyqtSignal()

    def __init__(self, imgs, url, method, parent = None):
        super().__init__(parent)
        self.images = imgs
        self.support_url = url
        self.method = method
        from pathlib import Path
        pathToDir = Path().absolute()
        self.path = os.path.join(pathToDir, self.support_url.split('.')[0])
        if not os.path.exists(self.path):
            os.mkdir(self.path)

    def run(self):
        for link in self.images:
            name = os.path.join(self.path,link.split('/')[-1])
            try:
                with open(name, 'wb') as image:
                    response = requests.get(self.method+"//"+self.support_url+link,stream = True)
                    if response.ok:
                        image.write(response.content)
            except:
                print("error with "+name)
        self.finished.emit()



#Класс который выполняет парсинг дополнительных ссылок с основной страницы
class ParseRunnable(QObject):
#    сигнал сгенерится, когда все операции будут выполнены
    finished = pyqtSignal('QVariant')
#    Конструктор класса, сразу при создании экземпляра передаю метод запроса http или https
#    url основной страницы и ссылки которые нужно спарсить
    def __init__(self,url, parent = None):
        super().__init__(parent)
        respContainer = Utilities.get_response(url)
        self.isValid = not respContainer == None
        self.origin_url = ""
        if (respContainer != None):
            self.edges = {}
            split_url = url.split('/')
            for token in split_url:
                if '.' in token:
                    self.origin_url = token
                    break
            self.method = split_url[0]

            self.all_tags = [tag.name for tag in respContainer.soup.find_all()]
            self.links = Utilities.get_valid_links([link.get('href') for link in  respContainer.soup.find_all('a')],self.origin_url)
            self.edges = [[url, link] for link in self.links]
            self.images = Utilities.get_valid_links([tag.get('src') for tag in respContainer.soup.find_all('img')], self.origin_url)

#    Добавляем новые ссылки в конец массива, если ссылки нет в этом списке
    def search_for_new_links(self,new_links):
        for link in new_links:
            if link  not in self.links:
                self.links.append(link)

    def search_for_new_imgs(self,new_imgs):
        for img in new_imgs:
            if img not in self.images:
                self.images.append(img)

#    Эта функция выполняется в отдельном потоке, ищет все тэги ро всем ссылкам
    def run(self):
        for link in self.links:
            url = self.method+"//"+self.origin_url+link
            respContainer = Utilities.get_response(url)
            if respContainer!= None:
                new_tags = [tag.name for tag in respContainer.soup.find_all()]
                links = Utilities.get_valid_links([link.get('href') for link in  respContainer.soup.find_all('a')], self.origin_url)
                new_nodes = [[link, llink] for llink in links]
                self.edges = [*self.edges, *new_nodes]
                self.search_for_new_links(links)
                self.all_tags = [*self.all_tags, *new_tags]
                imgs = Utilities.get_valid_links([tag.get('src') for tag in respContainer.soup.find_all('img')],self.origin_url)
                if (len(imgs) > 0):
                    self.search_for_new_imgs(imgs)
        self.links, self.edges = Utilities.unquote(self.links, self.edges)
        print(self.images)
#        вызываю сигнал, чтобы из вспомогательного потока передать данные в основной.

        self.finished.emit(self.all_tags)
#        print(self.images)



class Parser(QObject):
    finished = pyqtSignal()

    def __init__(self, parent = None):
        return super().__init__(parent)

#    pyqtSlot декоратор, который позволяет вызывать метод класса из qml файла, если объект класса есть в контексте.
#    Если у функции нет декоратора, то она не видна в qml файле
    @pyqtSlot(str, result = 'QVariant')
    def parse_html(self, url):
        self.runnable = ParseRunnable(url)
        self.origin_url = self.runnable.origin_url
        self.method = self.runnable.method
        return self.runnable.isValid

#    Выполняется когда закончит выполнение поток в котором парсится сайт
    def on_parse_finished(self, all_tags):
#        записываю словарь тегов
        self.tag_dict = Utilities.get_tags_count(all_tags)
#        print(self.runnable.nodes)
        self.links = self.runnable.links
        self.edges = self.runnable.edges
        self.images = self.runnable.images
#        Генерирую сигнал, который потом перехвачу в qml
        self.finished.emit()

#    Функция которую вызываю в qml для получения словаря. Tag - count
    @pyqtSlot(result = 'QVariant')
    def get_stat(self):
        return self.tag_dict

    @pyqtSlot()
    def show_graph(self):
        self.drawrunnable = DrawRunnable(self.links, self.edges)
        self.draw_thread = QThread()
        self.drawrunnable.moveToThread(self.draw_thread)
        self.draw_thread.started.connect(self.drawrunnable.run)
        self.drawrunnable.finished.connect(self.draw_thread.quit)
        self.drawrunnable.finished.connect(self.draw_thread.deleteLater)
        self.drawrunnable.finished.connect(self.drawrunnable.deleteLater)
        self.draw_thread.start()
#        Utilities.draw_graph(self.links, self.edges)

#    Функция вызывается из qml, чтобы запустить парсинг сайта
    @pyqtSlot()
    def get_tags_stats(self):
#        Создаю экземпляр класса потока
        self.thread  = QThread()
#        Переношу объект в поток (По сути никакого переноса нет, просто все методы класса будут выполняться в этом потоке)
        self.runnable.moveToThread(self.thread)
#        Соединяю все сигналы и слоты. Можно представить это как колбэки. То есть, есть сигнал, когда этот сигнал вызывается
#        все связанные с ним слоты выполняется. Это конечно не совсем так, но принцип примерно такой
#        Здесь я по сути говорю, что когда запустится поток, выполни метод run у класса runnable
#        Когда runnable закончит выполнение останови поток и удали объект потока, затем передай данные в основной класс и удали объект runnable
        self.runnable.finished.connect(self.on_parse_finished)
        self.thread.started.connect(self.runnable.run)
        self.runnable.finished.connect(self.thread.quit)
        self.runnable.finished.connect(self.thread.deleteLater)
        self.runnable.finished.connect(self.runnable.deleteLater)
#        Запускаю поток
        self.thread.start()

    @pyqtSlot()
    def download_images(self):
        self.download_thread= QThread()
        self.downloadrunnable = DownloadRunnable(self.images,self.origin_url,self.method)
        self.downloadrunnable.moveToThread(self.download_thread)
        self.download_thread.started.connect(self.downloadrunnable.run)
        self.downloadrunnable.finished.connect(self.download_thread.quit)
        self.downloadrunnable.finished.connect(self.download_thread.deleteLater)
        self.downloadrunnable.finished.connect(self.downloadrunnable.deleteLater)
#        Запускаю поток
        self.download_thread.start()




