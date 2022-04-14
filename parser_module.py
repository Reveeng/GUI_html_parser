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

'''Чтобы использовать создаем экземпляр класса, затем вызываем функцию parse_html(url)
где url ссылка на нужный нам сайт. В атрибуте last_repsonse будет лежать полученный html документ.
В атрибуте soup будет лежать объект BeautifulSoup
Чтобы получить статистику по тэгам html документа вызовите parser.get_all_tags()
'''


#Класс который выполняет парсинг дополнительных ссылок с основной страницы
class ParseRunnable(QObject):
#    сигнал сгенерится, когда все операции будут выполнены
    finished = pyqtSignal('QVariant')
#    Конструктор класса, сразу при создании экземпляра передаю метод запроса http или https
#    url основной страницы и ссылки которые нужно спарсить
    def __init__(self,method, url, links):
        super().__init__()
        self.origin_url = url
        self.links = links
        self.method = method
#    Сюда дописываю тэги найденные на основной странице
    def set_tags(self,tags):
        self.all_tags = tags
#    Эта функция выполняется в отдельном потоке, ищет все тэги ро всем ссылкам
    def run(self):
        for link in self.links:
            respContainer = Utilities.get_response(self.method+"//"+self.origin_url+link)
            if respContainer!= None:
                new_tags = [tag.name for tag in respContainer.soup.find_all()]
                self.all_tags = [*self.all_tags, *new_tags]
#        вызываю сигнал, чтобы из вспомогательного потока передать данные в основной.
        self.finished.emit(self.all_tags)


class Parser(QObject):
    finished = pyqtSignal()

    def __init__(self, parent = None):
        return super().__init__(parent)

#    pyqtSlot декоратор, который позволяет вызывать метод класса из qml файла, если объект класса есть в контексте.
#    Если у функции нет декоратора, то она не видна в qml файле
    @pyqtSlot(str, result = 'QVariant')
    def parse_html(self, url):
#        Получаю контейнер ответа, см файл Utilities
        respContainer = Utilities.get_response(url)
#        Проверяю получил ли ответ. Если ответ получен выполняем функцию, если нет, то ничего не делаем
        if (respContainer  != None):
            self.last_repsonse = respContainer.response
            self.soup = respContainer.soup
#            Получаю основной адрес сайта и метод
            split_url = url.split('/')
            for token in split_url:
                if '.' in token:
                    self.origin_url = token
                    break
            self.method = split_url[0]
            return True
        else:
            return False

#    Выполняется когда закончит выполнение поток в котором парсится сайт
    def on_parse_finished(self, all_tags):
#        записываю словарь тегов
        self.tag_dict = Utilities.get_tags_count(all_tags)
#        Генерирую сигнал, который потом перехвачу в qml
        self.finished.emit()

#    Функция которую вызываю в qml для получения словаря. Tag - count
    @pyqtSlot(result = 'QVariant')
    def get_stat(self):
        return self.tag_dict

#    Функция вызывается из qml, чтобы запустить парсинг сайта
    @pyqtSlot()
    def get_tags_stats(self):
#        Получаю ссылки и тэги с основной страницы
        links = [link.get('href') for link in  self.soup.find_all('a')]
        all_tags = [tag.name for tag in self.soup.find_all()]
        origin_links = Utilities.get_valid_links(links, self.origin_url)
#        создаю класс который будет парсить вторичные ссылки
        self.runnable = ParseRunnable(self.method,self.origin_url,origin_links)
#        выставляю уже найденные тэги
        self.runnable.set_tags(all_tags)
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
    def get_all_images(self):
        images = self.soup.find_all(['svg', 'img'])



