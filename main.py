# This Python file uses the following encoding: utf-8
import sys
import os

#Импорты Qt Классов
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtQml import QQmlApplicationEngine
#Импорт класса парсера
from parser_module import Parser
import Utilities

if __name__ == "__main__":
#    создается экземпляр класса приложения
    app = QGuiApplication(sys.argv)
#    Создается объект движка который будет разбирать qml файлы и отрисовывать по ним приложение
    engine = QQmlApplicationEngine()
#    Создается класс парсера
    parser = Parser()
#    передаю объект парсера в контекст движка, чтобы в qml файлах мог обращаться к функциям этого объекта
    engine.rootContext().setContextProperty("parser", parser)
#    загружаю основной файл с qml разметкой в движок
    engine.load(os.path.join(os.path.dirname(__file__), "main.qml"))
#    Проверяется есть ли рут объект в файле qml, по сути проверяют не пустой ли он. Если пустой выполнение заканчивается
    if not engine.rootObjects():
        sys.exit(-1)
#    Запускается цикл отрисовки приложения. Ну или просто входим в бескконечный цикл, который будет работть пока мы руками не закроем программу или она не упадет
    sys.exit(app.exec_())
