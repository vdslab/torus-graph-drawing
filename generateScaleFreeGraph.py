import networkx as nx
import os
import json

new_dir_path = './scallFreeGraph2/'

if not os.path.isdir(new_dir_path):
    os.mkdir(new_dir_path)

for i in range(1):
    n = 1000
    G = nx.scale_free_graph(n)
    undirected_G = G.to_undirected()
    largest_cc = max(nx.connected_components(undirected_G), key=len)
    largest_sub_graph = undirected_G.subgraph(largest_cc).copy()
    scale_free_graph = nx.Graph(largest_sub_graph)
    for j in scale_free_graph.nodes:
        if scale_free_graph.has_edge(j,j):
            scale_free_graph.remove_edge(j,j)
    data = nx.node_link_data(scale_free_graph)
    path = os.getcwd()

    with open(path + "/"+new_dir_path + str(n) + "-" + str(i) +".json", "w") as f:
        json.dump(data, f)