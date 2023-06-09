import json
from networkx.readwrite import json_graph
from algorithm.kamadaKawaiBase import kameKame, torusKameCenter
from common import log, drawGraph
import setup

filename = './graph/les_miserables.json'
graph = json_graph.node_link_graph(json.load(open(filename)))

all_log = {"file": filename}


def create_kk_graph(graph, filename):
    len_list = setup.get_len()
    all_log = {"file": filename}
    for _len in len_list:
        width = _len
        height = _len
        wh_log = {}
        print(_len)
        term = setup.get_term()
        for i in range(term):
            setup.init()
            setup.set_roop1(1000)

            time = setup.get_time()
            kameKame.kamada_kawai(graph, width, height)
            torusKameCenter.torus_kame(graph, width, height)

            drawGraph.create_compare_fig()

            _log = log.get_log()
            wh_log[str(time)] = _log

            message = str(time)
            print(message)

        all_log[str(_len)] = wh_log

    log.clear()
    time = setup.get_time()
    log.create_log(all_log)
