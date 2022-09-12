'''
Calculate the total simulation time in seconds
'''
def total_process_time(simulation_path, graph):
        total_process_time = 0
        for node in simulation_path:
            node_data = graph.nodes.data()[node]
            if node_data['type'] == 'operation' or node_data['type'] == 'wait':
                total_process_time += int(node_data['time'])
        return total_process_time

'''
Calculate the number of operations done by the given actor
'''
def number_of_operations(actor, simulation_path, graph):
    count = 0
    for node in simulation_path:
        node_data = graph.nodes.data()[node]
        if node_data['type'] == 'operation':
            if node_data['actor'] == actor:
                count += 1
    return count

'''
Calculate the activity time during the simulation of the given actor
'''
def time_of_activity(actor, simulation_path, graph):
    time = 0
    for node in simulation_path:
        node_data = graph.nodes.data()[node]
        if node_data['type'] == 'operation':
            if node_data['actor'] == actor:
                time += int(node_data['time'])
    return time