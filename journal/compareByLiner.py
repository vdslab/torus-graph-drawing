import collections
import csv
import glob
import math
import re
import sys
from pathlib import Path
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import egraph as eg
import networkx as nx

sys.path.append(str(Path(__file__).parent.parent) + "/")

from networkx.readwrite import json_graph
import json


"""
最適なセルサイズでの描画は、美的指標が良くなる←最適なセルサイズでの描画結果を、chenと比較
"""


class Weighting:
    def __init__(self, graph, size):
        self.graph = graph
        self.size = size

    def __call__(self, e):
        u, v = self.graph.edge_endpoints(e)
        u_set = set(self.graph.neighbors(u))
        v_set = set(self.graph.neighbors(v))
        return (len(u_set | v_set) - len(u_set & v_set)) / self.size


def torus_dist(u, v, size):
    x_list = [v[0] - size, v[0], v[0] + size]
    y_list = [v[1] - size, v[1], v[1] + size]

    best_pos = [v[0], v[1]]
    _dist = float("inf")

    for x in x_list:
        for y in y_list:
            ax = u[0] - x
            ay = u[1] - y
            adist = (ax**2 + ay**2) ** 0.5
            if _dist > adist:
                best_pos[0] = ax
                best_pos[1] = ay
                _dist = adist

    return _dist


def calc_gabiel_property(pos, graph):
    gp = 0
    for i, j in graph.edges:
        for v in graph.nodes:
            if i == v or j == v:
                continue
            pos_i = pos[str(i)]
            pos_j = pos[str(j)]
            pos_v = pos[str(v)]
            r_ij = math.hypot(pos_i[0] - pos_j[0], pos_i[1] - pos_j[1]) / 2
            c_ij = [(pos_i[0] + pos_j[0]) / 2, (pos_i[1] + pos_j[1]) / 2]
            d = r_ij - math.hypot(pos_v[0] - c_ij[0], pos_v[1] - c_ij[1])
            if d > 0:
                # 円の内側にノードがあるのでペナルティ
                gp += max(0, d**2)
            # gp += max(0, d**2)

    return gp


def neighborhood_preservation(pos, graph):
    dist = [[[float("inf"), i] for i in range(len(pos))] for j in range(len(pos))]
    node_name = [str(k) for k in graph.nodes.keys()]
    for i in range(len(pos) - 1):
        for j in range(i + 1, len(pos)):
            pos_i = pos[node_name[i]]
            pos_j = pos[node_name[j]]
            d = math.hypot(pos_i[0] - pos_j[0], pos_i[1] - pos_j[1])
            dist[i][j][0] = d
            dist[j][i][0] = d

    np = 0
    for v in graph.nodes:
        v_index = node_name.index(str(v))
        degree = graph.degree(v)
        sorted_d = sorted(dist[v_index], key=lambda x: x[0])
        knn = set([i for value, i in sorted_d[:degree]])
        rinsetu = set(nx.all_neighbors(graph, v))
        jaccard = len(knn & rinsetu) / len(knn | rinsetu)

        np += jaccard
    np /= len(graph.nodes)
    return np


def calc_edge_length_variance(pos, original_graph, multiple_num, weigthing=False):
    graph = eg.Graph()
    indices = {}
    for u in original_graph.nodes:
        indices[u] = graph.add_node(u)
    for u, v in original_graph.edges:
        graph.add_edge(indices[u], indices[v], (u, v))

    if weigthing:
        d = eg.all_sources_dijkstra(graph, Weighting(graph, 1))
    else:
        d = eg.all_sources_dijkstra(graph, lambda _: 1)

    diameter = max(
        d.get(u, v) for u in graph.node_indices() for v in graph.node_indices()
    )

    size = diameter * multiple_num

    dist_array = []
    for i, j in original_graph.edges:
        pos_i = pos[str(i)]
        pos_j = pos[str(j)]
        # torus なら torus上の距離でやらないといけない
        d = torus_dist(pos_i, pos_j, size)
        # d = math.hypot(pos_i[0] - pos_j[0], pos_i[1] - pos_j[1])
        dist_array.append(d)
    d_avg = sum(dist_array) / len(original_graph.edges)
    elv = 0
    for d in dist_array:
        elv += (d - d_avg) ** 2
    return elv / (len(original_graph.edges))


def calc_minimum_angle(pos, graph):
    # for v in graph.nodes:
    #     neighbors = nx.all_neighbors(graph, v)
    # print(neighbors)
    # ideal_theta = 360 / len(neighbors)
    # exit()
    return


def get_avg_metrics(data):
    stress = []
    ec = []
    iel = []
    cam = []
    nr = []

    for d in data:
        stress.append(d["stress"])
        ec.append(d["edge_crossings"])
        iel.append(d["ideal_edge_lengths"])
        cam.append(d["crossing_angle_maximization"])
        nr.append(d["node_resolution"])

    n = len(data)
    obj = {
        "stress": sum(stress) / n,
        "ec": sum(ec) / n,
        "iel": sum(iel) / n,
        "cam": sum(cam) / n,
        "nr": sum(nr) / n,
    }
    return obj


def get_median_data_metrics(data):
    stress = []
    n = len(data)
    for d in data:
        stress.append(d["stress"])

    sorted_stress = sorted(stress)
    best_idx = stress.index(sorted_stress[n // 2])

    obj = {
        "stress": data[best_idx]["stress"],
        "edge_crossings": data[best_idx]["edge_crossings"],
        "ideal_edge_lengths": data[best_idx]["ideal_edge_lengths"],
        "crossing_angle_maximization": data[best_idx]["crossing_angle_maximization"],
        "node_resolution": data[best_idx]["node_resolution"],
    }
    return obj


def get_median_metrics(data, rename=False):
    stress = []
    ec = []
    iel = []
    cam = []
    nr = []

    if rename == "True":
        for d in data:
            stress.append(d["stress"])
            ec.append(d["edge_crossings"])
            iel.append(d["ideal_edge_lengths"])
            cam.append(d["crossing_angle_maximization"])
            nr.append(d["node_resolution"])
    else:
        for d in data:
            stress.append(d["stress"])
            ec.append(d["edge_crossings"])
            iel.append(d["edge_length_vaiance"])
            cam.append(d["minimum_angle"])
            nr.append(d["node_resolution"])

    sorted_stress = sorted(stress)
    sorted_ec = sorted(ec)
    sorted_iel = sorted(iel)
    sorted_cam = sorted(cam)
    sorted_nr = sorted(nr)

    n = len(data)
    obj = {
        "stress": sorted_stress[n // 2],
        "edge_crossings": sorted_ec[n // 2],
        "ideal_edge_lengths": sorted_iel[n // 2],
        "crossing_angle_maximization": sorted_cam[n // 2],
        "node_resolution": sorted_nr[n // 2],
    }
    return obj


def get_rate(chen, optimal, name="name", _type="-"):
    obj = dict()
    flg = True
    for key in chen.keys():
        if optimal[key] == 0:
            if chen[key] == 0:
                obj[key] = 1
            # ※ 比で表してるのが良くなかったりする？
            elif key == "edge_crossings":
                obj[key] = (chen[key] + 1) / 1
            else:
                # ここどうするべき？
                obj[key] = 1.5
                # obj[key] = 10 * chen[key]
        else:
            obj[key] = chen[key] / optimal[key]
        if obj[key] < 0.75:
            flg = True

    if flg:
        print(name, _type, obj)
        print("------------------")

    return obj


def show_box_plot(data, title):
    # データフレームの作成
    df = pd.DataFrame(data)

    # データを長い形式に変換
    df_melted = df.melt(var_name="Key", value_name="Value")

    # for c_name in df.columns:
    #     df_c = df[c_name]
    #     # ボックスプロットの作成
    #     plt.figure(figsize=(10, 6))
    #     sns.boxplot(df_c, showfliers=False)
    #     plt.title(title + " " + c_name)
    #     plt.ylabel("rate (chen/optimal)")
    #     plt.axhline(y=1.0, color="red")
    #     plt.axhline(y=0.9, color="blue")
    #     plt.show()

    # ボックスプロットの作成
    plt.figure(figsize=(10, 6))
    sns.boxplot(x="Key", y="Value", data=df_melted, showfliers=False, color="white")
    plt.title(title)
    plt.ylabel("rate (chen/optimal)")
    plt.axhline(y=1.0, color="blue", ls="--")
    # plt.axhline(y=0.9, color="blue", ls="--", label="rate 0.9")
    # plt.axhline(y=1.1, color="blue", label="rate 1.1")
    # plt.legend()
    plt.show()


def download_csv(data):
    with open("weigthing_random.csv", mode="w", newline="") as file:
        # 辞書のキーをフィールド名として使用
        fieldnames = data[0].keys()  # ["name", "age", "city"]

        writer = csv.DictWriter(file, fieldnames=fieldnames)

        # ヘッダーを書き込み
        writer.writeheader()

        # データ行を書き込み
        writer.writerows(data)


def list2dict(data):
    data_dict = {}
    for d in data:
        data_dict.update(d)
    return data_dict


def findStopCellSize(data):
    stress = []
    for k, value in data.items():
        s = []
        for d in value:
            s.append(d["stress"])
        sorted_s = sorted(s)
        stress.append([sorted_s[len(sorted_s) // 2], k])

    stop_len = 5

    for i in range(len(stress) - stop_len):
        find = True
        for j in range(stop_len):
            if abs(stress[i][0] - stress[i + j][0]) > stress[i][0] * 0.025:
                find = False
                break
        if find:
            return stress[i][1]


"""
chen_files, optimal_files, renamed_optimal_file = True/False, weigthing_optimal = True/False

python3 journal/compareChenOptimal.py ./journal/data/chen/chen_torus_cell_size_networkx/log ./optimal_weigthing_networkx_0625/log True
"""


def main():
    args = sys.argv
    optimal_liner_files = glob.glob(args[1] + "/*")
    uniform = args[2]

    optimal_liner_files = [
        # "./journal/data/weigthing_liner/networkx/log/*",
        # "./journal/data/weigthing_liner/douh/log/*",
        # "./journal/data/weigthing_liner/dough0920/log/*",
        "./journal/data/weigthing_liner/random/log/*",
        "./journal/data/weigthing_liner/random0920/log/*",
        # "./test_liner_weighting_sparse/log/*",
        # "./journal/data/weigthing_liner/sparse0929/log/*",
        "./journal/data/weigthing_liner/test_random_1014/log/*",
    ]

    # optimal_liner_files = [
    #     "./journal/data/liner/douh/log/*",
    # "./journal/data/liner/networkx/log/*",
    #     "./journal/data/liner/random/log/*",
    #     # "./no_weigthing_liner_sparse/log/*",
    #     "./graphDrawing/data/egraph/liner_egraph_sparse_20/log/*",
    # ]

    graph_files = [
        # "./graphSet0920/networkx/*",
        # "./graphSet0920/doughNetGraph/default/*",
        # "./graphSet0920/doughNetGraph0920/*",
        # "./graphSet0920/randomPartitionNetwork /*",
        "./graphSet0920/randomPartitionNetwork0920/*",
        # "./graphSet0920/suiteSparse/*",
        # "./graphSet0920/suiteSparse0920/*",
        "./random_test_1014/*",
    ]

    graph_dict = {}
    for gf in graph_files:
        files = glob.glob(gf)
        for f in files:
            graph = json_graph.node_link_graph(json.load(open(f)))
            file_name = re.split("[/]", f)[-1][:-5]
            graph_dict[file_name] = graph

    with open("./graphSet0920/info_weigthed.json") as f:
        # with open("./graphSet/info202405_egraph.json") as f:
        # _graph_info = json.load(f)
        _graph_info = [g for g in json.load(f).values()]

    graph_info = list2dict(_graph_info)
    print(graph_info)

    # with open("./graphSet/chen_weighting_cell_size.json") as f:
    with open("./graphSet0920/chen_weighting_cell_size_median.json") as f:
        chen_cell_size_info = json.load(f)
    results = {}

    chen_size_dict = {}
    csv_data = []

    for files_name in optimal_liner_files:
        files = glob.glob(files_name)
        for file in files:
            with open(file) as f:
                data = json.load(f)
            name = re.split("[/]", file)[-1][:-6]
            print(name)

            if uniform == "True":
                diameter = nx.diameter(graph)
                chen_cell_size = (max(diameter, 2) + 1) / diameter
                digit2 = ((chen_cell_size * 10) // 1) / 10
                if not (str(chen_cell_size) in data["data"]):
                    diff = chen_cell_size - digit2
                    if diff < 0.03:
                        chen_cell_size = digit2
                    elif diff < 0.07:
                        chen_cell_size = digit2 + 0.05
                    else:
                        chen_cell_size = digit2 + 0.1
                    chen_cell_size = ((chen_cell_size * 100) // 1) / 100
                    print("re", name, chen_cell_size)
            elif name in chen_cell_size_info:
                chen_cell_size = chen_cell_size_info[name]
            else:
                graph = eg.Graph()
                indices = {}
                for u in graph_dict[name].nodes:
                    indices[u] = graph.add_node(u)
                for u, v in graph_dict[name].edges:
                    graph.add_edge(indices[u], indices[v], (u, v))

                d = eg.all_sources_dijkstra(graph, Weighting(graph, 1))
                diameter = max(
                    d.get(u, v)
                    for u in graph.node_indices()
                    for v in graph.node_indices()
                )
                edge_array = [
                    d.get(indices[u], indices[v]) for u, v in graph_dict[name].edges
                ]
                d_sum = sum(edge_array)
                # どうとるかで結構変わる？変わらない？
                d_avg = d_sum / len(graph_dict[name].edges)
                chen_cell_size = (max(diameter, 2) + d_avg) / diameter
                # chen_cell_size = "1.0"  # , int(chen_cell_size * 100) // 100
                digit2 = ((chen_cell_size * 10) // 1) / 10
                print(digit2)
                chen_cell_size = ((chen_cell_size * 100) // 1) / 100
                print(chen_cell_size)

                if not (str(chen_cell_size) in data["data"]):
                    diff = chen_cell_size - digit2
                    if diff < 0.03:
                        chen_cell_size = digit2
                    elif diff < 0.07:
                        chen_cell_size = digit2 + 0.05
                    else:
                        chen_cell_size = digit2 + 0.1
                    chen_cell_size = ((chen_cell_size * 100) // 1) / 100
                    print("re", chen_cell_size)

            chen_size_dict[name] = chen_cell_size

            if not name in graph_info:
                graph_info[name] = {"type": "none"}
                # print("skip", name)
                # continue

            optimal_cell_size = data["optimal_cell_size"]

            print(chen_cell_size, optimal_cell_size)

            # res_optimal = get_avg_metrics(data["data"][str(optimal_cell_size)])
            res_optimal = get_median_metrics(
                data["data"][str(optimal_cell_size)], "True"
            )
            # res_chen = get_avg_metrics(
            #     data["data"][str(chen_cell_size)]
            # )
            res_chen = get_median_metrics(data["data"][str(chen_cell_size)], "True")
            results[name] = {}
            results[name]["optimal"] = res_optimal
            results[name]["chen"] = res_chen
            results[name]["type"] = graph_info[name]["type"]
            rate_res = get_rate(
                results[name]["chen"],
                results[name]["optimal"],
                name,
                results[name]["type"],
            )
            csv_obj = rate_res
            csv_obj["name"] = name
            csv_obj["chen"] = chen_cell_size
            csv_obj["optimal"] = optimal_cell_size
            csv_obj["type"] = graph_info[name]["type"]
            csv_data.append(csv_obj)
            results[name]["rate"] = rate_res

    print("chen size dict", chen_size_dict)

    download_csv(csv_data)
    # exit()

    """
    比率での比較結果
    """
    _results = {}
    for key in results.keys():
        if "rate" in results[key]:
            _results[key] = results[key]

    types = [d["type"] for d in results.values()]
    c = collections.Counter(types)
    print(c)

    type_a_rate_data = [
        d["rate"] for d in list(filter(lambda x: x["type"] == "a", _results.values()))
    ]

    print(type_a_rate_data)

    show_box_plot(type_a_rate_data, "No-TORUS")

    type_b_rate_data = [
        d["rate"] for d in list(filter(lambda x: x["type"] == "b", _results.values()))
    ]
    show_box_plot(type_b_rate_data, "TORUS")

    type_c_rate_data = [
        d["rate"] for d in list(filter(lambda x: x["type"] == "c", _results.values()))
    ]
    show_box_plot(type_c_rate_data, "c")

    exit()


if __name__ == "__main__":
    main()
