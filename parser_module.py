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
    progressChanged = pyqtSignal('QVariant')

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
        img_numb = 0
        img_progr = 0
#        names = []
        for link in self.images:
            img_numb += 1
            img_progr = (img_numb)/len(self.images)
            self.progressChanged.emit(img_progr)
            name = os.path.join(self.path,link.split('/')[-1])
#            print(link)
            try:
                with open(name, 'wb') as image:
                    response = requests.get(link,stream = True)
                    if response.ok:
                        image.write(response.content)
#                        names.append(url)
            except:
                print("error with "+name)
#        print(names)
        self.finished.emit()



#Класс который выполняет парсинг дополнительных ссылок с основной страницы
class ParseRunnable(QObject):
#    сигнал сгенерится, когда все операции будут выполнены
    finished = pyqtSignal('QVariant')
    progressChanged = pyqtSignal('QVariant')
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
            self.links, out_links = Utilities.get_valid_links([link.get('href') for link in  respContainer.soup.find_all('a')],
                                                    self.method,self.origin_url)
            self.edges = [[url, link] for link in self.links]
            out_nodes = [[url, link] for link in out_links]
            self.edges = [*self.edges, *out_nodes]

            self.images, _ = Utilities.get_valid_links([tag.get('src') for tag in respContainer.soup.find_all('img')],
                                                    self.method,self.origin_url)
            hide_imgs = Utilities.search_img_by_re(respContainer.response)
            Utilities.concatenate_nd(self.images, hide_imgs)
#    Добавляем новые ссылки в конец массива, если ссылки нет в этом списке
#    def search_for_new_links(self,new_links):
#        for link in new_links:
#            if link  not in self.links:
#                self.links.append(link)

#    def search_for_new_imgs(self,new_imgs):
#        for img in new_imgs:
#            if img not in self.images:
#                self.images.append(img)

#    Эта функция выполняется в отдельном потоке, ищет все тэги ро всем ссылкам
    def run(self):
        link_numb = 0
        old_link_progr = 0
        for link in self.links:
            respContainer = Utilities.get_response(link)
            if respContainer!= None:
                new_tags = [tag.name for tag in respContainer.soup.find_all()]
                links, out_links = Utilities.get_valid_links([link.get('href') for link in  respContainer.soup.find_all('a')],
                                                   self.method,self.origin_url)
                new_nodes = [[link, llink] for llink in links]
                out_nodes = [[link, llink] for llink in out_links]
                self.edges = [*self.edges, *new_nodes, *out_nodes]
                Utilities.concatenate_nd(self.links, links)
#                self.search_for_new_links(links)
                self.all_tags = [*self.all_tags, *new_tags]
                imgs,out_img = Utilities.get_valid_links([tag.get('src') for tag in respContainer.soup.find_all('img')],
                                                  self.method,self.origin_url)
                if (len(imgs) > 0):
                    Utilities.concatenate_nd(self.images, imgs)
                    Utilities.concatenate_nd(self.images, out_img)
                hide_imgs = Utilities.search_img_by_re(respContainer.response)
                Utilities.concatenate_nd(self.images, list(hide_imgs))
                link_numb += 1
                tmp_prgr = (link_numb)/len(self.links)
                if (tmp_prgr > old_link_progr):
                    old_link_progr = tmp_prgr
                    self.progressChanged.emit(old_link_progr)
#        hide_imgs = Utilities
        self.links, self.edges = Utilities.unquote(self.links, self.edges)
#        вызываю сигнал, чтобы из вспомогательного потока передать данные в основной.

        self.finished.emit(self.all_tags)
#        print(self.images)



class ParserModel(QObject):
    finished = pyqtSignal()
    parseProgressChanged = pyqtSignal('QVariant')
    downloadProgressChanged = pyqtSignal('QVariant')
    imageDownloaded = pyqtSignal()
    getAllImagesUrl = pyqtSignal('QVariant')
    stateChanged = pyqtSignal('QVariant')

    def __init__(self, parent = None):
        return super().__init__(parent)

#    Выполняется когда закончит выполнение поток в котором парсится сайт
    def on_parse_finished(self, all_tags):
#        записываю словарь тегов
        self.tag_dict = Utilities.get_tags_count(all_tags)
        self.tag_count = len(all_tags)
        self.links = self.runnable.links
        self.edges = self.runnable.edges
        self.images = self.runnable.images
        self.getAllImagesUrl.emit(self.images)
        name = self.origin_url.split('.')[0]
        self.download_images()
        Utilities.save_as_csv(name, self.tag_dict)
#        Генерирую сигнал, который потом перехвачу в qml
        self.finished.emit()

#    Функция которую вызываю в qml для получения словаря. Tag - count
    @pyqtSlot(result = 'QVariant')
    def get_stat_results(self):
        sub_len = int(len(self.tag_dict)/3)
        tags_1 = dict(list(self.tag_dict.items())[:sub_len-1])
        tags_2 = dict(list(self.tag_dict.items())[sub_len:2*sub_len-1])
        tags_3 = dict(list(self.tag_dict.items())[2*sub_len:3*sub_len-1])
        tags = [tags_1,tags_2, tags_3]
        return tags

    @pyqtSlot(result = 'QVariant')
    def get_tags_count(self):
        return self.tag_count

    @pyqtSlot()
    def show_graph(self):
        self.setState("Идет построение графа")
        self.drawrunnable = DrawRunnable(self.links, self.edges)
        self.draw_thread = QThread()
        self.drawrunnable.moveToThread(self.draw_thread)
        self.draw_thread.started.connect(self.drawrunnable.run)
        self.drawrunnable.finished.connect(self.draw_thread.quit)
        self.drawrunnable.finished.connect(self.draw_thread.deleteLater)
        self.drawrunnable.finished.connect(self.drawrunnable.deleteLater)
        self.drawrunnable.finished.connect(lambda : self.setState("Построение графа закончено"))
        self.draw_thread.start()


    @pyqtSlot(str, result = 'QVariant')
    def parse_html(self, url):
        self.runnable = ParseRunnable(url)
        self.origin_url = self.runnable.origin_url
        self.method = self.runnable.method
        if not self.runnable.isValid:
            return false
#    def get_tags_stats(self):
        self.setState("Парсинг начат")
#        Создаю экземпляр класса потока
        self.thread  = QThread()
#        Переношу объект в поток (По сути никакого переноса нет, просто все методы класса будут выполняться в этом потоке)
        self.runnable.moveToThread(self.thread)
#        Соединяю все сигналы и слоты. Можно представить это как колбэки. То есть, есть сигнал, когда этот сигнал вызывается
#        все связанные с ним слоты выполняется. Это конечно не совсем так, но принцип примерно такой
#        Здесь я по сути говорю, что когда запустится поток, выполни метод run у класса runnable
#        Когда runnable закончит выполнение останови поток и удали объект потока, затем передай данные в основной класс и удали объект runnable
        self.runnable.finished.connect(self.on_parse_finished)
        self.runnable.progressChanged.connect(self.parseProgressChanged)
        self.thread.started.connect(self.runnable.run)
        self.runnable.finished.connect(self.thread.quit)
        self.runnable.finished.connect(self.thread.deleteLater)
        self.runnable.finished.connect(self.runnable.deleteLater)
        self.runnable.finished.connect(lambda : self.setState("Парсинг закончен"))
#        Запускаю поток
        self.thread.start()
        return True

    def download_images(self):
        self.setState("Начата загрузка изображений")
        self.download_thread= QThread()
        self.downloadrunnable = DownloadRunnable(self.images,self.origin_url,self.method)
        self.downloadrunnable.moveToThread(self.download_thread)
        self.download_thread.started.connect(self.downloadrunnable.run)
        self.downloadrunnable.finished.connect(self.imageDownloaded)
        self.downloadrunnable.progressChanged.connect(self.downloadProgressChanged)
        self.downloadrunnable.finished.connect(self.download_thread.quit)
        self.downloadrunnable.finished.connect(lambda : self.setState("Загрузка изображений закончена"))
#        self.downloadrunnable.finished.connect(self.download_thread.deleteLater)
        self.downloadrunnable.finished.connect(self.downloadrunnable.deleteLater)
#        Запускаю поток
        self.download_thread.start()

    def setState(self,state):
        if state != "":
            self.stateChanged.emit(state)


