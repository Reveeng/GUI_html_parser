# This Python file uses the following encoding: utf-8

import plotly.graph_objects as go
import networkx as nx

if __name__ == "__main__":
    import pandas as pd
    import plotly.plotly as py
    from plotly.graph_objs import *
    import networkx as nx

    matrix = pd.read_csv("matrix.csv", sep = "\t", index_col = 0, header = 0)

    G = nx.DiGraph()

    # add nodes:
    G.add_nodes_from(matrix.columns)

    # add edges:
    edge_lst = [(i,j, matrix.loc[i,j])
                for i in matrix.index
                for j in matrix.columns
                if matrix.loc[i,j] != 0]
    G.add_weighted_edges_from(edge_lst)

    # create node trace:
    node_trace = Scatter(x = [], y = [], text = [], mode = 'markers',
                        marker = Marker(
                        showscale = True,
                        colorscale = 'YIGnBu',
                        reversescale = True,
                        color = [],
                        size = [],
                        colorbar = dict(
                            thickness = 15,
                            title = 'Node Connections',
                            xanchor = 'left',
                            titleside = 'right'),
                        line = dict(width = 2)))

    # set node positions
    pos = nx.spring_layout(G)
    for node in G.nodes():
        G.node[node]['pos']= pos[node]

    for node in G.nodes():
        x, y = G.node[node]['pos']
        node_trace['x'].append(x)
        node_trace['y'].append(y)

    # create edge trace:
    edge_trace = Scatter(x = [], y = [], text = [],
                         line = Line(width = [], color = '#888'),
                         mode = 'lines')

    for edge in G.edges():
        x0, y0 = G.node[edge[0]]['pos']
        x1, y1 = G.node[edge[1]]['pos']
        edge_trace['x'] += [x0, x1, None]
        edge_trace['y'] += [y0, y1, None]
        edge_trace['text'] += str(matrix.loc[edge[0], edge[1]])[:5]

    # size nodes by degree
    deg_dict = {deg[0]:int(deg[1]) for deg in list(G.degree())}
    for node, degree in enumerate(deg_dict):
        node_trace['marker']['size'].append(deg_dict[degree] + 20)

    fig = Figure(data = Data([edge_trace, node_trace]),
                 layout = Layout(
                     title = '<br>AA Substitution Rates',
                     titlefont = dict(size = 16),
                     showlegend = True,
                     margin = dict(b = 20, l = 5, r = 5, t = 40),
                     annotations = [dict(
                         text = "sub title text",
                         showarrow = False,
                         xref = "paper", yref = "paper",
                         x = 0.005, y = -0.002)],
                     xaxis = XAxis(showgrid = False,
                                   zeroline = False,
                                   showticklabels = False),
                     yaxis = YAxis(showgrid = False,
                                   zeroline = False,
                                   showticklabels = False)))

    py.plot(fig, filename = 'networkx')
