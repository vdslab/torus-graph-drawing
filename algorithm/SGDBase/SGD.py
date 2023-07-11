import math
from common import drawGraph
from common import log
from common import calcDrawInfo, debug
import setup
import itertools
import numpy as np
import networkx
from common import initGraph


def sgd(graph, _width=None, _height=None):
    edge_weight = setup.get_edge_width()
    node_len = len(graph.nodes)
    node2num = initGraph.get_node2num_memoized(graph)

    # 隣接行列の初期化
    d = [[float('inf')]*node_len for i in range(node_len)]
    # 隣接行列の作成
    for i in range(node_len):
        d[i][i] = 0
    for x_node, y_node in graph.edges:
        # 重みがないので1
        x = node2num[x_node]
        y = node2num[y_node]
        d[x][y] = edge_weight
        d[y][x] = edge_weight

    # ワーシャルフロイド(最短経路)
    for k in range(node_len):
        for i in range(node_len):
            for j in range(node_len):
                d[i][j] = min(d[i][j], d[i][k]+d[k][j])

    # print("fin わーシャル")

    # w_ij=dij^(-2)
    w = [[1]*node_len for i in range(node_len)]
    for i in range(node_len):
        for j in range(node_len):
            if d[i][j] != 0:
                w[i][j] = pow(d[i][j], -2)

    maxd = 0
    for i in range(node_len):
        for j in range(i, node_len):
            if maxd < d[i][j]:
                maxd = d[i][j]

    height = maxd if _height == None else _height
    width = maxd if _width == None else _width

    # 隣接行列の初期化
    l = [[0]*node_len for i in range(node_len)]

    # 隣接行列の初期化
    k = [[0]*node_len for i in range(node_len)]

    for i in range(node_len):
        for j in range(node_len):
            if i == j:
                continue
            l[i][j] = d[i][j]
            k[i][j] = 1/(d[i][j]*d[i][j])

    pos = calcDrawInfo.get_pos(node_len, width, height)

    loop1, loop2 = setup.get_loop()

    # loop=100くらいがちょうど良さそう
    eps = 0.1
    eta_max = 1/(min(list(itertools.chain.from_iterable(w))))
    eta_min = eps/(max(list(itertools.chain.from_iterable(w))))
    eta = eta_max
    _lamda = -1*math.log(eta_min/eta_max)/loop1

    debug.add_node_a(pos)

    for t in range(loop1):
        # pair_index = [list(p) for p in itertools.combinations(
        #     [i for i in range(node_len)], 2)]
        # np.random.shuffle(pair_index)
        pair_index = calcDrawInfo.get_random_pair(node_len, loop1, t)
        eta = eta_max*pow(math.e, -1*_lamda*t)

        for i, j in pair_index:
            mu = w[i][j]*eta
            if mu > 1:
                mu = 1
            rx = (calcDrawInfo.dist(pos, i, j)-d[i][j])/2 * \
                (pos[i][0]-pos[j][0])/calcDrawInfo.dist(pos, i, j)
            ry = (calcDrawInfo.dist(pos, i, j)-d[i][j])/2 * \
                (pos[i][1]-pos[j][1])/calcDrawInfo.dist(pos, i, j)

            pos[i][0] = pos[i][0]-mu*rx
            pos[i][1] = pos[i][1]-mu*ry
            pos[j][0] = pos[j][0]+mu*rx
            pos[j][1] = pos[j][1]+mu*ry

    delta = calcDrawInfo.calc_delta(pos, k, l, node_len)
    edge_score = [(d[node2num[u]][node2num[v]] -
                  calcDrawInfo.dist(pos, node2num[u], node2num[v]))**2 for u, v in graph.edges]
    drawGraph.draw_graph(graph, pos, delta, edge_score,
                         node_len, "SGD", width, height)
    kame_log = log.calc_evaluation_values(delta, edge_score)

    log.add_log("SGD", kame_log)

    return kame_log["dist"]["sum"]
