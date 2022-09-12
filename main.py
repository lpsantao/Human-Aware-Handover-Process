import argparse
import glob, os
from simulation.simulation import Simulation
from collab_operator.collab_operator import Operator
from utilities.read_write import *
from MQTT_connect import MQQT_client

broker_address = 'localhost'
broker_port = 1883
topic_id = "DataNea/HumanID"

if __name__ == "__main__":

    # Read and parse the arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--gp", type=str,
                        default="C:\\Users\\X580\\PycharmProjects\\SP1Prot4\\resources\\graphs\\simple_graph.json",
                        required=False, help="initial graph file path")
    parser.add_argument("--fgf", type=str, default="test_graph.json", required=False,
                        help="file name to save the final graph obtained from the simulation")
    parser.add_argument("--bom", type=str, default="C:\\Users\\X580\\PycharmProjects\\SP1Prot4\\resources\\BoM.txt",
                        required=False, help="bill of materials file path")
    parser.add_argument("--ipp", type=str,
                        default="C:\\Users\\X580\\PycharmProjects\SP1Prot4\\resources\\initial_poses_roller.txt",
                        required=False, help="initial objects' poses file path")
    parser.add_argument("--fpp", type=str,
                        default="C:\\Users\\X580\\PycharmProjects\SP1Prot4\\resources\\final_poses_roller.txt",
                        required=False, help="final objects' poses file path")
    parser.add_argument("--oe", type=int, required=False,
                        help="operator expertise: 0 - beginner, 1 - intermediate, 2 - professional")
    parser.add_argument("--am", type=str, default="automatic", required=False,
                        help="automation mode: 'automatic', 'mixed' or 'manual'")
    args = parser.parse_args()

    '''
    mqtt = MQQT_client()
    mqtt.new_message.clear()
    mqtt.connect(broker_address, broker_port)
    mqtt.client.subscribe(topic_id)
    human_id = mqtt.read_mqtt(topic_id)
    '''
    graph_file_id = None
    humanid = '23'
    os.chdir("C:\\Users\\X580\\PycharmProjects\\SP1Prot4\\resources\\graphs")
    human_id = "*" + humanid + ".json"
    fgname = "simple_graph_" + humanid + ".json"
    print(fgname)
    for graph_id in glob.glob(human_id):
        graph_file_id = graph_id

    if graph_file_id is not None:
        print('LOADING EXISTING GRAPH')
        graph = read_json_graph(graph_file_id)
    else:
        print('LOADING NEW GRAPH')
        graph = read_json_graph(args.gp)

    if graph is not None:
        bom = read_bill_of_materials(args.bom)
        initial_poses = read_poses(args.ipp)
        final_poses = read_poses(args.fpp)

        operator = Operator(graph, args.oe)
        simulation = Simulation(graph, operator, args.am, bom, initial_poses, final_poses)
        updated_graph, task, simulation_path = simulation.init_simulation()
        log_simulation(task, simulation_path, args.am, updated_graph)
        write_graph_to_file(updated_graph, fgname)
