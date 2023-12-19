import networkx as nx
import egraph as eg
import matplotlib.pyplot as plt
from common  import drawEgraph, aestheticsMeasures, initGraph

def torus_sgd(original_graph, file_name, multiple_num=1.0, random_idx=0, time="xxxx"):
    graph = eg.Graph()
    indices = {}
    for u in original_graph.nodes:
        indices[u] = graph.add_node(u)
    for u, v in original_graph.edges:
        graph.add_edge(indices[u], indices[v], (u, v))

    size = nx.diameter(original_graph) * multiple_num

    d = eg.all_sources_bfs(
        graph,
        1 / size, # edge length
    )
    drawing = eg.DrawingTorus.initial_placement(graph)
    rng = eg.Rng.seed_from(random_idx)  # random seed
    sgd = eg.FullSgd.new_with_distance_matrix(d)
    scheduler = sgd.scheduler(
        100,  # number of iterations
        0.1,  # eps: eta_min = eps * min d[i, j] ^ 2
    )

    def step(eta):
        # print(eg.stress(drawing, d))
        sgd.shuffle(rng)
        sgd.apply(drawing, eta)
    scheduler.run(step)

    s = eg.stress(drawing, d)

    pos = {u: (drawing.x(i) , drawing.y(i)) for u, i in indices.items()}

    maxd = initGraph.get_maxd(original_graph, file_name, True, 1/size)
    d = initGraph.get_shortest_path(original_graph, file_name, True, 1/size)
    log = aestheticsMeasures.calc_egraph_torus_evaluation_values(original_graph, pos, maxd, d, 1/size)
    log["multiple_num"] = multiple_num
    log["stress"] = s
    log["pos"] = pos

    drawEgraph.torus_graph_drawing(pos, original_graph, file_name, multiple_num, time, False)
    exit()

    return log