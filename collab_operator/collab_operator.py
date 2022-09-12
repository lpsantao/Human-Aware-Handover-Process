import random
import networkx as nx

OPERATIONS = ['fasten']

class Operator:
    def __init__(self, graph, expertise):
        self.expertise = expertise
        self.estimate_operation_time(graph)

    def estimate_operation_time(self, graph):
        try:
            for node_idx,node_data in graph.nodes.data():
                node_data = graph.nodes.data()[node_idx]
                if node_data['type'] == 'operation':
                    if self.expertise == 1:   
                        if node_data['operation'] == "pick":
                            nx.set_node_attributes(graph, {node_idx:random.randrange(2, 3, 1)}, 'time_operator')
                            nx.set_node_attributes(graph, {node_idx:0.05}, 'op_error_rate')
                        elif node_data['operation'] == "place":
                            nx.set_node_attributes(graph, {node_idx:random.randrange(2, 3, 1)}, 'time_operator')
                            nx.set_node_attributes(graph, {node_idx:0.05}, 'op_error_rate')
                        elif node_data['operation'] == "snap":
                            nx.set_node_attributes(graph, {node_idx:random.randrange(3, 5, 1)}, 'time_operator')
                            nx.set_node_attributes(graph, {node_idx:0.1}, 'op_error_rate')
                        elif node_data['operation'] == "position":
                            nx.set_node_attributes(graph, {node_idx:random.randrange(3, 5, 1)}, 'time_operator')
                            nx.set_node_attributes(graph, {node_idx:0.07}, 'op_error_rate')
                        elif node_data['operation'] == "fasten":
                            nx.set_node_attributes(graph, {node_idx:random.randrange(6, 8, 1)}, 'time_operator')
                            nx.set_node_attributes(graph, {node_idx:0.1}, 'op_error_rate')
                    elif self.expertise == 2:  
                        if node_data['operation'] == "pick":
                            nx.set_node_attributes(graph, {node_idx:random.randrange(1, 3, 1)}, 'time_operator')
                            nx.set_node_attributes(graph, {node_idx:0.03}, 'op_error_rate')
                        elif node_data['operation'] == "place":
                            nx.set_node_attributes(graph, {node_idx:random.randrange(1, 3, 1)}, 'time_operator')
                            nx.set_node_attributes(graph, {node_idx:0.03}, 'op_error_rate')
                        elif node_data['operation'] == "snap":
                            nx.set_node_attributes(graph, {node_idx:random.randrange(2, 4, 1)}, 'time_operator')
                            nx.set_node_attributes(graph, {node_idx:0.07}, 'op_error_rate')
                        elif node_data['operation'] == "position":
                            nx.set_node_attributes(graph, {node_idx:random.randrange(2, 4, 1)}, 'time_operator')
                            nx.set_node_attributes(graph, {node_idx:0.05}, 'op_error_rate')
                        elif node_data['operation'] == "fasten":
                            nx.set_node_attributes(graph, {node_idx:random.randrange(4, 6, 1)}, 'time_operator')
                            nx.set_node_attributes(graph, {node_idx:0.07}, 'op_error_rate')
                    else:
                        if node_data['operation'] == "pick":
                            nx.set_node_attributes(graph, {node_idx:random.randrange(2, 4, 1)}, 'time_operator')
                            nx.set_node_attributes(graph, {node_idx:0.07}, 'op_error_rate')
                        elif node_data['operation'] == "place":
                            nx.set_node_attributes(graph, {node_idx:random.randrange(2, 4, 1)}, 'time_operator')
                            nx.set_node_attributes(graph, {node_idx:0.07}, 'op_error_rate')
                        elif node_data['operation'] == "snap":
                            nx.set_node_attributes(graph, {node_idx:random.randrange(3, 7, 1)}, 'time_operator')
                            nx.set_node_attributes(graph, {node_idx:0.2}, 'op_error_rate')
                        elif node_data['operation'] == "position":
                            nx.set_node_attributes(graph, {node_idx:random.randrange(3, 7, 1)}, 'time_operator')
                            nx.set_node_attributes(graph, {node_idx:0.15}, 'op_error_rate')
                        elif node_data['operation'] == "fasten":
                            nx.set_node_attributes(graph, {node_idx:random.randrange(7, 10, 1)}, 'time_operator')
                            nx.set_node_attributes(graph, {node_idx:0.2}, 'op_error_rate')
        except nx.NetworkXException:
            print("There is a problem with the nodes of the graph")
