# Coded by Aleksandr Rodionov
# rexarrior@yandex.ru

# imports---------------------------------------------------------------
import networkx as nx
# License: BSD license

import matplotlib.pyplot as plt
# License: matplotlib licence
# http://matplotlib.sourceforge.net/users/license.html

# methods---------------------------------------------------------------


def visualize_link_graph(graph, nodeSize=2000, fontSize=9,
                         pictureSize=(20, 20)):
    '''
    Visualize and show the graph of decision links.
    nodeSize - int, size of node on the graph's picture
    fontSize - int, size of font of the graph's nodes labels
    pictureSize - tuple of size of the graph's picture in inches
    '''
    nodes = graph[0]
    edges = graph[1]

    # filling the graph
    nxGraph = nx.DiGraph()
    for node in nodes:
        nxGraph.add_node(node, node_size=nodeSize)

    nxGraph.add_edges_from(edges)

    # drawing the graph
    plt.figure(figsize=pictureSize)
    pos = nx.spring_layout(nxGraph)
    nx.draw_networkx_nodes(nxGraph, pos,  node_size=nodeSize)
    labels = {node: node for node in nodes}
    nx.draw_networkx_labels(graph, pos, labels,
                            font_size=fontSize, font_color='b')
    nx.draw_networkx_edges(nxGraph, pos)
    plt.show()
