import networkx as nx
import sys
import json
from networkx.readwrite import json_graph

'''
Read graph from the given json file path
'''


def read_json_graph(file_path):
    try:
        # read json file
        with open(file_path, "r") as graph_file:
            graph_data = json.loads(graph_file.read())
    except OSError as err:
        print("OS error: {0}".format(err))
    except json.decoder.JSONDecodeError:
        print("There was a problem reading the json file.")
    else:
        # transform data into a graph
        graph = json_graph.node_link_graph(graph_data)
        return graph


'''
Write graph to the given json file path
'''


def write_graph_to_file(graph, graph_file):
    graph_path = 'resources/graphs/' + graph_file
    try:
        with open(graph_path, "w") as graph_file:
            # transform graph into a json format
            graph_json = json_graph.node_link_data(graph)
            # write into file
            graph_file.write(json.dumps(graph_json))
    except OSError as err:
        print("OS error: {0}".format(err))


'''
Set attribute of a graph's node given the graph, the id of the node, the attribute and the new atribute value
'''


def set_attribute(graph_path, node_idx, attribute, value):
    graph = read_json_graph(graph_path)
    nx.set_node_attributes(graph, {node_idx: value}, attribute)
    node = graph.nodes.data()[node_idx]
    print(node)
    write_graph_to_file(graph, graph_path)


'''
Set attribute of a graph's sequential subtasks, given the graph, the attribute and the new atribute value
'''


def set_attribute_sequential(graph_path, attribute, value):
    graph = read_json_graph(graph_path)
    for node_idx, node_data in graph.nodes(data=True):
        if node_data['type'] == 'subtask' and node_data['sequence'] == 'sequential':
            nx.set_node_attributes(graph, {node_idx: value}, attribute)
            print(graph.nodes.data()[node_idx])
    write_graph_to_file(graph, graph_path)


'''
Set attribute of a graph's parallel subtasks, given the graph, the attribute and the new atribute value
'''


def set_attribute_parallel(graph_path, attribute, value):
    graph = read_json_graph(graph_path)
    for node_idx, node_data in graph.nodes(data=True):
        if node_data['type'] == 'subtask' and node_data['sequence'] == 'parallel':
            nx.set_node_attributes(graph, {node_idx: value}, attribute)
            print(graph.nodes.data()[node_idx])
    write_graph_to_file(graph, graph_path)


'''
Get attribute of a graph's node given the graph, the id of the node and the attribute
'''


def get_attribute(graph_path, node_idx, attribute):
    graph = read_json_graph(graph_path)
    print(graph.nodes.data()[node_idx][attribute])


'''
Get all attributes of a graph's node given the graph and the id of the node
'''


def get_attributes(graph_path, node_idx):
    graph = read_json_graph(graph_path)
    print(graph.nodes.data()[node_idx])


if __name__ == '__main__':
    try:
        globals()[sys.argv[1]](sys.argv[2], sys.argv[3])
    except:
        globals()[sys.argv[1]](sys.argv[2], sys.argv[3], sys.argv[4])
