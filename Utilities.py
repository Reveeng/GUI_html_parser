# This Python file uses the following encoding: utf-8

from multiprocessing.dummy import Pool
import numpy as np
import requests
from bs4 import BeautifulSoup
import networkx as nx
import matplotlib

matplotlib.use('WebAgg')

import matplotlib.pyplot as plt

from PyQt5 import QtWidgets

#Заголовок для запросов
header = {'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'}

all_tags = ["!--...--","!DOCTYPE","a","abbr","acronym", "address",
            "applet","area","article","aside","audio","b",
            "base","basefont","bdi","bdo","big","blockquote",
            "body","br","button","canvas","caption","center",
            "cite","code","col","colgroup","data","datalist",
            "dd","del","details","dfn","dialog","dir","div",
            "dl","dt","em","embed","fieldset","figcaption",
            "figure","font","footer","form","frame","frameset",
            "h1","h2","h3","h4","h5","h6","head","header","hr",
            "html","i","iframe","img","input","ins","kbd",
            "label","legend","li","link","main","map","mark",
            "meta","meter","nav","noframes","noscript","object",
            "ol","optgroup","option","output","p","param","picture",
            "pre","progress","q","rp","rt","ruby","s","samp","script",
            "section","select","small","source","span","strike",
            "strong","style","sub","summary","sup","svg","table",
            "tbody","td","template","textarea","tfoot","th","thead"
            "time","title","tr","track","tt","u","ul","var","video","wbr"]


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
    clear_links = get_unique_array(clear_links)
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
#    unique_tags = get_unique_array(tags)
#    valid_tags = []
#    for tag in unique_tags:
#        if tag in all_tags:
#            valid_tags.append(tag)
    tag_dict = {}
    for tag in all_tags:
        tag_dict[tag] = tags.count(tag)
    return tag_dict


def unquote(links, edges):
    from urllib.parse import unquote as unq
    links = [unq(link) for link in links]
    edges = [[unq(edge[0]),unq(edge[1])] for edge in edges]
    return links, edges

#nodes - ноды графы, edges - массив типа [node,node] устанавливает ребро между нодами
def draw_graph(nodes,edges):
#    создаю объъект графа

    G = nx.Graph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)


    import plotly.graph_objects as go
    pos = nx.spring_layout(G)
    nodes_x = []
    nodes_y = []

    for node in G.nodes():
        G.nodes[node]['pos']= pos[node]

    for node in G.nodes():
        x, y = G.nodes[node]['pos']
        nodes_x.append(x)
        nodes_y.append(y)

    node_trace = go.Scatter(x = nodes_x, y = nodes_y, text = list(G.nodes()), mode = 'markers',
                        marker = go.scatter.Marker(
                        showscale = False,
                        colorscale = 'ylgnbu',
                        reversescale = False,
                        color = "black",
                        size = 5,
                        line = dict(width = 2)))


    edge_trace = go.Scatter(x = [], y = [], text = [],
                         line = go.scatter.Line(width = 1, color = '#888'),
                         mode = 'lines')


    for edge in G.edges():
        x0, y0 = G.nodes[edge[0]]['pos']
        x1, y1 = G.nodes[edge[1]]['pos']
        edge_trace['x'] += (x0, x1, None)
        edge_trace['y'] += (y0, y1, None)

    fig = go.Figure(data=[edge_trace, node_trace],
                 layout=go.Layout(
                    showlegend = False,
                    xaxis=dict(showgrid = False, zeroline = False, showticklabels = False),
                    yaxis=dict(showgrid = False, zeroline = False, showticklabels = False))
                    )
    fig.show()
