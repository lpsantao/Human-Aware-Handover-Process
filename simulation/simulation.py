import random
from collections import deque
import networkx as nx

from simulation.plot_graph import PlotGraph
from robot.robot_state import RobotState

from enum import Enum
import time
from collab_operator.collab_operator import OPERATIONS


class AutomationMode(Enum):
    AUTOMATIC = 'automatic'
    MIXED = 'mixed'
    MANUAL = 'manual'


class NodeType(Enum):
    TASK = "task"
    SUBTASK = "subtask"
    OPERATION = "operation"
    WAIT = "wait"


WAIT_TIME = 1


class Simulation:

    # TODO screwpack
    # funções para adicionar/mudar atributos a certos nós (por exemplo só a nós sequenciais)

    def __init__(self, graph, operator, automation_mode, cur_poses, final_poses):
        self.graph = graph
        self.operator = operator
        self.automation_mode = automation_mode

        self.total_process_time = 0
        self.objects_in_workspace = deque()
        self.simulation_path = deque()
        self.robot_state = RobotState(cur_poses, final_poses, graph)
        self.plot_graph = PlotGraph(graph)

    '''
    Initiate simulation
    '''

    def init_simulation(self):
        try:
            # Get the main task (root of the graph) and the final operations (leaves)
            self.source_task = \
                [[node_idx, self.graph.nodes.data()[node_idx]] for node_idx, degree in self.graph.in_degree() if
                 degree == 0][0]
            self.target_operations = [node_idx for node_idx, degree in self.graph.out_degree() if degree == 0]
        except AttributeError as err:
            print(err)
        else:
            # Get all possible paths from the root to the final operations
            all_paths = deque()
            for target_op in self.target_operations:
                try:
                    paths = list(nx.all_simple_paths(self.graph, self.source_task[0], target_op))
                except nx.NetworkXNoPath:
                    print("No path between nodes " + self.source_task[0] + " and " + target_op + " exists")

                # When there is more than 1 way to complete a subtask, choose the longest path
                if len(paths) > 1:
                    list_len = [len(i) for i in paths]
                    max_paths = [i for i in paths if len(i) == max(list_len)]
                    all_paths.append((max_paths))
                else:
                    all_paths.append(paths[0])

            if self.automation_mode == AutomationMode.AUTOMATIC.value or \
                    self.automation_mode == AutomationMode.MANUAL.value:
                self.define_operation_actor()
                # new_all_paths = self.add_wait_nodes(all_paths)
                self.simulate_manual_automatic(all_paths)
                return self.graph, self.source_task[1], self.simulation_path
            else:
                self.simulate()
                return self.graph

    '''
    Fully automatic or fully manual simulation
    '''
    def simulate_manual_automatic(self, all_paths):
        done_nodes = deque()
        all_paths = all_paths[0]
        while len(all_paths) > 1:
            print(len(all_paths))
            print('AHA_', all_paths)
            # Randomly choose a path
            possible_path = random.choice(all_paths)
            print('THIS: ', possible_path)
            if self.validate_sequence(possible_path):
                for node_idx in possible_path:
                    node_data = self.graph.nodes.data()[node_idx]
                    if node_data['type'] != NodeType.TASK.value:
                        self.simulation_path.append(node_idx)
                        if node_data['type'] == NodeType.SUBTASK.value:
                            current_subtask_idx = node_idx
                            current_subtask_object = node_data['object']
                        elif node_data['type'] == NodeType.WAIT.value:
                            done_nodes.append(node_idx)
                            self.graph_simulation(node_idx, done_nodes, node_data['time'])
                        elif node_data['type'] == NodeType.OPERATION.value:
                            if node_data['actor'] == 'operator':
                                self.graph_simulation(node_idx, done_nodes, node_data['time_operator'])
                            else:
                                self.graph_simulation(node_idx, done_nodes, node_data['time_robot'])
                                start_time = time.time()
                                self.robot_state.send_move_to_robot(node_idx, node_data, self.simulation_path,
                                                                    int(node_data['time_robot']))
                                end_time = time.time()
                                operation_time = start_time - end_time
                                done_nodes.append(node_idx)
                                # Update time atributte
                                nx.set_node_attributes(self.graph, {node_idx: operation_time}, 'time')
                                # possible_path.insert(possible_path.index(node_idx) + 1, node_idx)

                            if node_idx in self.target_operations:
                                successors = list(nx.nodes(nx.dfs_tree(self.graph, source=current_subtask_idx)))[1:]

                                if all(succ in self.simulation_path for succ in successors):
                                    self.objects_in_workspace.append(current_subtask_object)
                                    done_nodes.append(current_subtask_idx)

                                    # ERROR NODE
                            if node_data['actor'] == 'operator' and random.random() <= node_data['op_error_rate']:
                                error_times = 1
                                if 'error' in node_data:
                                    error_times += node_data['error']
                                nx.set_node_attributes(self.graph, {node_idx: {'error': error_times}})
                                # Redo de operation
                                possible_path.insert(possible_path.index(node_idx) + 1, node_idx)
                all_paths.remove(possible_path)

    '''
    Validate a path
    '''

    def validate_sequence(self, sequence):
        # TODO position
        for node_idx in sequence[:-1]:
            node_data = self.graph.nodes.data()[node_idx]

            if node_data['type'] == NodeType.SUBTASK.value and node_data['operation'] == 'bring':
                return True
            elif node_data['type'] == NodeType.OPERATION.value:
                op_object = node_data['object']
                if op_object not in self.objects_in_workspace:
                    return False
                if op_object == "screw" and node_data['operation'] == "fasten" and 'screwdriver' \
                        not in self.objects_in_workspace:
                    return False

        return True

    '''
    If the actor between two consecutive operations within a subtask is diferent,
     add a node to represent the waiting time needed to switch the actor
    '''

    def add_wait_nodes(self, all_paths):
        for path in all_paths:
            print(path)
            for node_idx in path:
                node_data = self.graph.nodes.data()[node_idx]
                # If node is not the last one check if the actor for the next node is different
                if node_data['type'] == NodeType.OPERATION.value and node_idx not in self.target_operations:
                    next_node_idx = path[path.index(node_idx) + 1]
                    next_node_data = self.graph.nodes.data()[next_node_idx]
                    if next_node_data['type'] == NodeType.OPERATION.value and \
                            next_node_data['actor'] != node_data['actor']:
                        self.graph.remove_edge(node_idx, next_node_idx)
                        wait_node = 'wait_' + node_idx + '_' + next_node_idx
                        self.graph.add_node(wait_node, type='wait', time=WAIT_TIME)
                        self.graph.add_edges_from([(node_idx, wait_node), (wait_node, next_node_idx)])
                        path.insert(path.index(next_node_idx), wait_node)
        return all_paths

    '''
    Define the working nodes and call the function that plots the graph
    '''

    def graph_simulation(self, node_idx, done_nodes, wait_time):
        working_nodes = deque()
        working_nodes.append(node_idx)

        # If an operation is on working mode, its respective subtask and task are also on working mode
        predecessors = list(nx.nodes(nx.dfs_tree(self.graph.reverse(), source=node_idx).reverse()))[1:]
        for node in predecessors:
            node_data = self.graph.nodes.data()[node]
            if node_data['type'] == NodeType.TASK.value or node_data['type'] == NodeType.SUBTASK.value:
                working_nodes.append(node)

        self.plot_graph.flush_plot(working_nodes, done_nodes, wait_time)

    '''
    Define the operation's actor if the Simulation is fully manual or automatic
    '''

    def define_operation_actor(self):
        for node_idx, node_data in self.graph.nodes.data():
            if node_data['type'] == NodeType.OPERATION.value:
                if self.automation_mode == AutomationMode.AUTOMATIC.value:
                    if node_data['operation'] in OPERATIONS:
                        nx.set_node_attributes(self.graph, {node_idx: 'operator'}, 'actor')
                    else:
                        nx.set_node_attributes(self.graph, {node_idx: 'robot'}, 'actor')
                elif self.automation_mode == AutomationMode.MANUAL.value:
                    nx.set_node_attributes(self.graph, {node_idx: 'operator'}, 'actor')

    def simulate(self):
        print("Starting dynamic simulation")
