import networkx as nx
from egraph import Graph, DrawingTorus, Rng, FullSgd
import matplotlib.pyplot as plt
from common.drawEgraph import torus_graph_drawing



def main():
    nx_graph = nx.moebius_kantor_graph()
    graph = Graph()
    indices = {}
    for u in nx_graph.nodes:
        indices[u] = graph.add_node(u)
    for u, v in nx_graph.edges:
        graph.add_edge(indices[u], indices[v], (u, v))

    size = nx.diameter(nx_graph)*1.5 # ここで変わる
    drawing = DrawingTorus.initial_placement(graph)
    rng = Rng.seed_from(0)  # random seed
    sgd = FullSgd(
        graph,
        lambda _: 1 / size,  # edge length
    )
    scheduler = sgd.scheduler(
        100,  # number of iterations
        0.1,  # eps: eta_min = eps * min d[i, j] ^ 2
    )

    def step(eta):
        sgd.shuffle(rng)
        sgd.apply(drawing, eta)
    scheduler.run(step)

    pos = {u: (drawing.x(i), drawing.y(i)) for u, i in indices.items()}
    # nx.draw(nx_graph, pos)
    # plt.savefig('tmp/torus_sgd.png')

    torus_graph_drawing(pos, nx_graph, "test", False)


if __name__ == '__main__':
    main()