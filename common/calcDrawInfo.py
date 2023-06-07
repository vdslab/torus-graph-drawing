import random
import math
import itertools
import numpy as np

POS = []
PAIR_INDEX = []


def clear():
    global POS, PAIR_INDEX
    POS = []
    PAIR_INDEX = []


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


def dist(pos, u, v):
    dx = pos[u][0] - pos[v][0]
    dy = pos[u][1] - pos[v][1]
    return (dx ** 2 + dy ** 2) ** 0.5


def dist_around(pos, u, v, width, height):
    # uが中心
    d = dist(pos, u, v)

    ax = pos[u][0] - ((pos[v][0]-(pos[u][0]-width/2) +
                       width) % width+(pos[u][0]-width/2))
    ay = pos[u][1] - ((pos[v][1]-(pos[u][1]-height/2) +
                       height) % height+(pos[u][1]-height/2))
    adist = (ax ** 2 + ay ** 2) ** 0.5
    return min(d, adist)


def dist_around_position(pos, u, v, width, height):
    # # 回り込みが発生しない場合
    d = dist(pos, u, v)
    d_around = dist_around(pos, u, v, width, height)
    # # print(d, d_around)
    # if d == d_around:
    #     return [pos[u][0]-pos[v][0], pos[u][1]-pos[v][1]]
    # else:
    #     print("around")
    # if abs(pos[u][0]-pos[v][0]) < 0.0000001 and abs(pos[u][1]-pos[v][1]) < 0.0000001:
    #     return [pos[u][0]-pos[v][0], pos[u][1]-pos[v][1]]
    if abs(d-d_around) < 0.00000001:
        return [pos[u][0]-pos[v][0], pos[u][1]-pos[v][1]]
    # print(abs("around", d-d_around))
    # uが中心
    ax = pos[u][0] - ((pos[v][0]-(pos[u][0]-width/2) +
                       width) % width+(pos[u][0]-width/2))
    ay = pos[u][1] - ((pos[v][1]-(pos[u][1]-height/2) +
                       height) % height+(pos[u][1]-height/2))
    return [ax, ay]


def init_pos(node_len, width, height):
    global POS
    L0 = 1
    # 範囲を固定
    l = 100
    for i in range(node_len):
        x = L0*random.uniform(width/2-l/2, width/2+l/2)
        y = L0*random.uniform(height/2-l/2, height/2+l/2)
        POS.append([x, y])


def get_pos(node_len, width, height):
    global POS
    if len(POS) == 0:
        init_pos(node_len, width, height)
    pos0 = [[x, y] for x, y in POS]
    return pos0


def dorakue(pos, width, height):
    # 先生の式のやつでやらないとダメかも？
    if pos[0] < 0:
        pos[0] = width*(abs(pos[0])//width+1)+pos[0]
        # print("dorakue")
    elif pos[0] > width:
        pos[0] = pos[0]-width*(abs(pos[0])//width)
        # print("dorakue")

    if pos[1] < 0:
        pos[1] = height*(abs(pos[1])//height+1)+pos[1]
        # print("dorakue")
    elif pos[1] > height:
        pos[1] = pos[1]-height*(abs(pos[1])//height)
        # print("dorakue")

    return pos


def shift_center(pos, idx, node_len, width, height):
    diff_x = pos[idx][0]-width/2
    diff_y = pos[idx][1]-height/2

    for i in range(node_len):
        pos[i][0] -= diff_x
        pos[i][1] -= diff_y
        pos[i] = dorakue(pos[i], width, height)

    return diff_x, diff_y, pos


def shift_flat(pos, diff_x, diff_y, node_len, width, height):
    for i in range(node_len):
        pos[i][0] += diff_x
        pos[i][1] += diff_y

        pos[i] = dorakue(pos[i], width, height)

    return pos


def calc_delta(pos,  k, l, node_len, width, height):
    Delta = [0]*node_len
    for i in range(node_len):
        Ex = 0
        Ey = 0
        diff_x, diff_y, pos = shift_center(pos, i, node_len, width, height)
        for j in range(node_len):
            if i == j:
                continue
            norm = math.sqrt((pos[i][0]-pos[j][0]) **
                             2 + (pos[i][1]-pos[j][1])**2)
            dx_ij = pos[i][0]-pos[j][0]
            dy_ij = pos[i][1]-pos[j][1]

            Ex += k[i][j]*dx_ij*(1.0-l[i][j]/norm)
            Ey += k[i][j]*dy_ij*(1.0-l[i][j]/norm)
        Delta[i] = math.sqrt(Ex*Ex+Ey*Ey)
        pos = shift_flat(pos, diff_x, diff_y, node_len, width, height)

    return Delta


def calc_delta_around(pos,  k, l, node_len, width, height):
    Delta = [0]*node_len
    for i in range(node_len):
        Ex = 0
        Ey = 0
        diff_x, diff_y, pos = shift_center(pos, i, node_len, width, height)
        for j in range(node_len):
            if i == j:
                continue
            norm = math.sqrt((pos[i][0]-pos[j][0]) **
                             2 + (pos[i][1]-pos[j][1])**2)

            dx_ij = pos[i][0] - ((pos[j][0]-(pos[i][0]-width/2) +
                                  width) % width+(pos[j][0]-width/2))
            dy_ij = pos[i][1] - ((pos[j][1]-(pos[i][1]-height/2) +
                                  height) % height+(pos[i][1]-height/2))

            Ex += k[i][j]*dx_ij*(1.0-l[i][j]/norm)
            Ey += k[i][j]*dy_ij*(1.0-l[i][j]/norm)
        Delta[i] = math.sqrt(Ex*Ex+Ey*Ey)
        pos = shift_flat(pos, diff_x, diff_y, node_len, width, height)
    return Delta


def init_pair_index(node_len, loop):
    global PAIR_INDEX
    for i in range(loop):
        pair_index = [list(p) for p in itertools.combinations(
            [i for i in range(node_len)], 2)]
        np.random.shuffle(pair_index)
        PAIR_INDEX.append(pair_index)


def get_random_pair(node_len, loop, t):
    global PAIR_INDEX
    if len(PAIR_INDEX) == 0:
        init_pair_index(node_len, loop)
    pair_index = [[x, y] for x, y in PAIR_INDEX[t]]
    return pair_index
