import networkx as nx
import matplotlib.pyplot as plt
from enum import Enum
from matplotlib.widgets import Button


class NodeColor(Enum):
    TODO = "Gainsboro"
    WORKING = "Khaki"
    DONE = "DarkSeaGreen"


class State(Enum):
    TODO = "todo"
    WORKING = "working"
    DONE = "done"

class Index:
    ind = 0

    def next(self, event):
        print("yolo")

class PlotGraph:
    def __init__(self, graph):
        self.callback = Index()
        self.graph = graph
        self.fig, self.ax = plt.subplots(figsize=(10, 7))
        self.node_size = 500
        self.node_shape = "o"
        self.edge_color = "gray"
        self.font_color = "black"
        self.font_size = 7
        axnext = plt.axes([0.81, 0.05, 0.1, 0.075])
        self.bnext = Button(axnext, 'Next')


        plt.ion()

    def flush_plot(self, working_nodes, done_nodes, wait_time):
        self.plot_graph(working_nodes, done_nodes)
        # sleeps
        plt.pause(2)

    '''
    Plot the graph
    '''
    def plot_graph(self, working_nodes, done_nodes):

        self.pos = nx.nx_agraph.graphviz_layout(self.graph, prog="dot")
        self.ax.clear()
        # Update nodes' states
        for node_idx in working_nodes:
            nx.set_node_attributes(
                self.graph, {node_idx: State.WORKING.value}, "state"
            )
        for node_idx in done_nodes:
            nx.set_node_attributes(
                self.graph, {node_idx: State.DONE.value}, "state"
            )

        # Edges
        nx.draw_networkx_edges(
            self.graph, pos=self.pos, ax=self.ax, edge_color=self.edge_color
        )

        # TO DO nodes
        nx.draw_networkx_nodes(
            self.graph,
            pos=self.pos,
            nodelist=self.graph.nodes() - set(working_nodes) - set(done_nodes),
            node_shape=self.node_shape,
            node_size=self.node_size,
            node_color=NodeColor.TODO.value,
            ax=self.ax,
        )

        # DONE nodes
        nx.draw_networkx_nodes(
            self.graph,
            pos=self.pos,
            nodelist=set(done_nodes),
            node_shape=self.node_shape,
            node_size=self.node_size,
            node_color=NodeColor.DONE.value,
            ax=self.ax,
        )

        # WORKING nodes
        nx.draw_networkx_nodes(
            self.graph,
            pos=self.pos,
            nodelist=set(working_nodes),
            node_shape=self.node_shape,
            node_size=self.node_size,
            node_color=NodeColor.WORKING.value,
            ax=self.ax,
        )

        # Nodes labels
        node_labels = {}
        for node_idx, node_data in self.graph.nodes.data():
            node_labels[node_idx] = node_data["type"]

            if node_data["type"] == "wait":
                node_labels[node_idx] += "\n" + str(node_data["time"]) + " sec"
            else:
                node_labels[node_idx] += (
                    "\n" + node_data["operation"] + " " + node_data["object"]
                )
                if node_data["type"] == "operation" or node_data["type"] == "error":
                    node_labels[node_idx] += "\nactor: " + node_data["actor"]
                    if node_idx in done_nodes:
                        node_labels[node_idx] += (
                            "\ntime: " + str(node_data["time"]) + " sec"
                        )
                    else:
                        time_actor = node_data["time_" + node_data["actor"]]
                        node_labels[node_idx] += (
                            "\nestimated time: " + str(time_actor) + " sec"
                        )
                else:
                    if "sequence" in node_data:
                        if node_data["sequence"] == "sequential":
                            node_labels[node_idx] += "\n>"
                        else:
                            node_labels[node_idx] += "\n||"

        nx.draw_networkx_labels(
            self.graph,
            pos=self.pos,
            labels=node_labels,
            font_color=self.font_color,
            font_size=self.font_size,
            ax=self.ax,
        )
        self.bnext.on_clicked(self.callback.next)
        self.ax.set_xticks([])
        self.ax.set_yticks([])
