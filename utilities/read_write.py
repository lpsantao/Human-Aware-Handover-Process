from networkx.readwrite import json_graph
import json
from utilities.calculate import *
'''
Log the final simulation
'''
def log_simulation(source_task, simulation_path, automation_mode, graph):
    file_log = open("C:\\Users\\X580\\PycharmProjects\\SP1Prot4\\resources/simulation.txt", "w")
    file_log.write("------- TASK " + source_task['operation'] + ' ' + source_task['object'] + " -------\n\nMode: " + automation_mode + " simulation\n")
    file_log.write("Total process time: " + str(total_process_time(simulation_path, graph)))
    number_operations = number_of_operations('operator', simulation_path, graph)
    file_log.write("\nNumber of operations performed by the operator: " + str(number_operations))
    number_operations = number_of_operations('robot', simulation_path, graph)
    file_log.write("\nNumber of operations performed by the robot: " + str(number_operations))
    time = time_of_activity('operator', simulation_path, graph)
    file_log.write("\nOperator activity time: " + str(time))
    time = time_of_activity('robot', simulation_path, graph)
    file_log.write("\nRobot activity time: " + str(time) + "\n")

    for node in simulation_path:
        node_data = graph.nodes(data=True)[node]
        if node_data['type'] == 'subtask':
            file_log.write("\n")
            file_log.write(node_data['type'] + " " + node_data['operation'] + ' ' + node_data['object'] + ": \n")
        elif node_data['type'] == 'wait':
            file_log.write("- " + node_data['type'] + " " + str(node_data['time']) + " seconds\n")
        elif 'error' in node_data:
            file_log.write("ERROR - " + node_data['operation'] + ' ' + node_data['object'] + " performed by the " + node_data[
                    'actor'] + " in " + str(node_data['time']) + " seconds\n")
        else:
            file_log.write(
                "- " + node_data['operation'] + ' ' + node_data['object'] + " performed by the " + node_data[
                    'actor'] + " in " + str(node_data['time']) + " seconds\n")

'''
Write graph to the given json file path
'''
def write_graph_to_file(graph, graph_file):
    graph_path = 'C:\\Users\\X580\\PycharmProjects\\SP1Prot4\\resources/graphs/' + graph_file
    try:
        with open(graph_path, "w") as graph_file:
            #transform graph into a json format
            graph_json = json_graph.node_link_data(graph)
            #write into file
            graph_file.write(json.dumps(graph_json))
    except OSError as err:
        print("OS error: {0}".format(err))

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
Read bill of materials from the given file
'''
def read_bill_of_materials(file_path):
    bom = dict()
    try:
        with open(file_path, "r") as bom_file:
            for line in bom_file:
                (key, val) = line.split()
                bom[key] = int(val)
    except OSError as err:
        print("OS error: {0}".format(err))
    else:
        return bom

'''
Read object poses from the given file
'''
def read_poses(file_path):
    poses = dict()
    try:
        with open(file_path, "r") as poses_file:
            for line in poses_file:
                key, val = line.split()
                val = list(val.split(","))
                val = [float(x) for x in val]
                poses[key] = val
    except OSError as err:
        print("OS error: {0}".format(err))
    else:
        return poses

