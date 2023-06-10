import json
from networkx.readwrite import json_graph
from algorithm.SGDBase import SGD, torusSGD
from common import log, drawGraph
import setup


filename = './graph/les_miserables.json'
print(filename)
graph = json_graph.node_link_graph(json.load(open(filename)))

len_list = [500, 750, 1000]
all_log = {"file": filename}

for _len in len_list:
    width = _len
    height = _len
    wh_log = {}
    print(_len)
    for i in range(10):
        setup.init()
        setup.set_roop1(50)

        time = setup.get_time()
        sgd = SGD.torus_sgd(graph, width, height)
        torus_sgd = torusSGD.torus_sgd(graph, width, height)
        drawGraph.create_compare_fig()

        _log = log.get_log()
        wh_log[str(time)] = _log

        message = str(time)
        print(message)

    all_log[str(_len)] = wh_log

log.clear()
time = setup.get_time()
log.create_log(all_log)