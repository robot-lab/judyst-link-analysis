# Coded by Aleksandr Rodionov
# rexarrior@yandex.ru

#imports-----------------------------------------------------------------------
import networkx as nx
import matplotlib.pyplot as plt

#methods-----------------------------------------------------------------------
def VisualizeLinkGraph(graph, nodeSize = 2000, fontSize = 9, pictureSize = (20, 20)):
    '''
    Visualize and show the graph of decision links.
    nodeSize - int, size of node on the graph's picture
    fontSize - int, size of font of the graph's nodes labels
    pictureSize - tuple of size of the graph's picture in inches
    '''
    nodes = graph[0]
    adjMatr = graph[1]

    #filling the graph
    nxGraph = nx.DiGraph()    
    for node in nodes:
        nxGraph.add_node(node, node_size = nodeSize)

    for i in range(len(adjMatr)):
        for j in range(len(adjMatr[0])):
            if (adjMatr[i][j]):
                nxGraph.add_edge(nodes[i], nodes[j])

    #drawing the graph
    plt.figure(figsize = pictureSize)
    pos = nx.spring_layout(nxGraph)
    nx.draw_networkx_nodes(nxGraph, pos,  node_size = nodeSize)
    labels = {node:node for node in nodes}
    nx.draw_networkx_labels(graph,pos,labels,font_size=fontSize, font_color="b")
    nx.draw_networkx_edges(nxGraph, pos)
    plt.show()
    

