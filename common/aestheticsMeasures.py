import calcDrawInfo
import math
import numpy as np


def calc_mean(array):
    return sum(array)/len(array)


def calc_sd(array):
    mean = calc_mean(array)
    return sum((score - mean)**2 for score in array)/len(array)


def calc_evaluation_values(delta, dist_score):
    delta_mean = calc_mean(delta)
    delta_sd = calc_sd(delta)
    delta_sum = sum(delta)

    dist_mean = calc_mean(dist_score)
    dist_sd = calc_sd(dist_score)
    dist_sum = sum(dist_score)

    return {"delta": {"mean": delta_mean, "sd": delta_sd, "sum": delta_sum},
            "dist": {"mean": dist_mean, "sd": dist_sd, "sum": dist_sum}}


def calc_edge_length_variance(pos, graph, node2num):
    l = []
    for x_node, y_node in graph.edges:
        u = node2num[x_node]
        v = node2num[y_node]
        l.append(calcDrawInfo.dist(pos, u, v))
    l_mean = calc_mean(l)
    variance = sum([((l_mean/l_mean) - (l[i]/l_mean))
                   ** 2 for i in range(l)])/len(l)
    return variance


def calc_deg(pos, u, v):
    x0, y0 = 0, 0
    vec1 = [pos[u][0]-x0, pos[u][1]-y0]
    vec2 = [pos[v][0]-x0, pos[v][1]-y0]
    absvec1 = np.linalg.norm(vec1)
    absvec2 = np.linalg.norm(vec2)
    inner = np.inner(vec1, vec2)
    cos_theta = inner/(absvec1*absvec2)
    theta = math.degrees(math.acos(cos_theta))
    return theta


def minimum_angle(pos,  l):
    _sum = 0
    for i in range(len(pos)):
        # 近接ノード
        near_i = [j for j, x in enumerate(l[i]) if x == 100]
        # 理想の角度
        ideal_theta = 360/len(near_i)
        # ある点を基準に角度をとる
        thetas_from_zero = []
        thetas = []
        for v in near_i:
            thetas_from_zero.append(calc_deg(pos, i, v))
        # ソートしないと隣同士の角度が取れないのでソート
        thetas_from_zero = sorted(thetas_from_zero, reverse=True)
        for j in range(1, len(thetas_from_zero)-1):
            thetas.append(thetas_from_zero[j+1]-thetas_from_zero[j])
        thetas.append(thetas_from_zero[0]+(360-thetas_from_zero[-1]))
        min_theta = min(thetas)
        _sum += abs(ideal_theta-min_theta)/ideal_theta
    return _sum/len(pos)
