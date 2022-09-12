import argparse
import glob
import logging
import os
import threading
import tkinter as tk
from tkinter import font as tkfont
from tkinter import messagebox, PhotoImage
from tkinter import ttk

from MQTT_connect import MQQT_client
from UR5API.data_secondary_client import *
from collab_operator.collab_operator import Operator
from simulation.simulation import Simulation
from utilities.read_write import *

broker_address = '192.168.0.7'
broker_port = 1883
topic_id = "DataNea/ID"
topic_request = "feup/ID"
topic_pose = "ubi/pose"
ids = None
exit_event = threading.Event()
with_nea = False


class MainUI(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title_font = tkfont.Font(family='Helvetica', size=16, weight="bold")
        self.title("Prototype 4 GUI")
        self.resizable(False, False)
        self.geometry("500x250")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.active_name = None
        container = tk.Frame(self)
        container.grid(sticky="nsew")
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.frames = {}
        page_name2 = PageOne.__name__
        frame2 = PageOne(parent=container, controller=self)
        self.frames[page_name2] = frame2
        frame2.grid(row=0, column=0, sticky="nsew")
        page_name = StartPage.__name__
        frame = StartPage(parent=container, controller=self, pageOne=frame2)
        self.frames[page_name] = frame
        frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame("StartPage")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Are you sure?"):
            self.destroy()
            exit_event.set()


class StartPage(tk.Frame):
    def __init__(self, parent, controller, pageOne=None):
        tk.Frame.__init__(self, parent)
        self.pageOne = pageOne
        self.buttonok = tk.Button(self.pageOne, text="OK", bg="#ffffff", fg="#263942",
                                  command=lambda: self.finished_id())
        self.pressed = False
        self.controller = controller
        self.ids = None
        render = PhotoImage(file='homepagepic.png')
        img = tk.Label(self, image=render)
        img.image = render
        img.grid(row=0, column=1, rowspan=4, sticky="nsew")
        label = tk.Label(self, text="        Initiate ID Process       ", font=self.controller.title_font, fg="#263942")
        label.grid(row=0, sticky="ew")
        button1 = tk.Button(self, text="   START  ", fg="#ffffff", bg="#263942",
                            command=lambda: [self.controller.show_frame("PageOne"),
                                             threading.Thread(target=self.get_id).start()])
        button3 = tk.Button(self, text="Quit", fg="#263942", bg="#ffffff", command=self.on_closing)
        button1.grid(row=1, column=0, ipady=3, ipadx=7)
        button3.grid(row=3, column=0, ipady=3, ipadx=32)

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Are you sure?"):
            self.controller.destroy()
            exit_event.set()

    def get_id(self):
        global ids
        self.pressed = False
        if with_nea:
            mqtt.client.publish(topic_request, 'START')
            time.sleep(1)
        while self.pressed is False:
            if exit_event.is_set():
                logging.warning('exit')
                break
            if with_nea:
                ids = mqtt.read_mqtt(topic_id)  # nea
            else:
                ids = "1"
            logging.info("ID of operator is %s", ids)
            if self.pageOne is not None:
                if self.pageOne.pb and ids is not None:
                    self.pageOne.pb.stop()
                    tk.Label(self.pageOne, text="Found your ID. Click OK when ready!", fg="#263942",
                             font='Helvetica 12 bold').grid(
                        row=0,
                        column=1,
                        pady=10,
                        padx=5)
                    self.pageOne.buttoncanc.grid_forget()
                    self.pageOne.buttoncanc.place_forget()
                    self.pageOne.buttoncanc.pack_forget()
                    self.buttonok.grid(row=3, column=1, pady=10, ipadx=5, ipady=4)
                    self.pressed = True

    def finished_id(self):
        self.controller.destroy()
        exit_event.set()
        '''
        self.buttonok.place_forget()
        self.buttonok.grid_forget()
        self.buttonok.pack_forget()
        tk.Label(self.pageOne, text="Please, look at the camera", fg="#263942", font='Helvetica 12 bold').grid(row=0,
                                                                                                               column=1,
                                                                                                               pady=10,
                                                                                                               padx=5)
        # progressbar
        self.pageOne.pb = ttk.Progressbar(self.pageOne, orient='horizontal', mode='indeterminate', length=280)
        self.pageOne.pb.grid(column=1, row=1, columnspan=2, padx=10, pady=20)
        self.pageOne.pb.start()
        self.pageOne.buttoncanc = tk.Button(self.pageOne, text="Cancel", bg="#ffffff", fg="#263942",
                                            command=lambda: [self.pageOne.cancel_id()])
        self.pageOne.buttoncanc.grid(row=3, column=1, pady=10, ipadx=5, ipady=4)
        self.controller.show_frame("StartPage")
        '''


class PageOne(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        tk.Label(self, text="Please, look at the camera", fg="#263942", font='Helvetica 12 bold').grid(row=0, column=1,
                                                                                                       pady=10, padx=5)
        # progressbar
        self.pb = ttk.Progressbar(self, orient='horizontal', mode='indeterminate', length=280)
        self.pb.grid(column=1, row=1, columnspan=2, padx=10, pady=20)
        self.pb.start()
        self.buttoncanc = tk.Button(self, text="Cancel", bg="#ffffff", fg="#263942",
                                    command=lambda: [self.cancel_id()])
        self.buttoncanc.grid(row=3, column=1, pady=10, ipadx=5, ipady=4)

    def cancel_id(self):
        self.controller.show_frame("StartPage")


if with_nea:
    mqtt = MQQT_client()
    mqtt.new_message.clear()
    mqtt.connect(broker_address, broker_port)
    mqtt.client.subscribe(topic_id)
    mqtt.client.subscribe(topic_pose)

app = MainUI()
app.mainloop()
graph_file_id = None
parser = argparse.ArgumentParser()
parser.add_argument("--gp", type=str,
                    default="C:\\Users\\X580\\PycharmProjects\\SP1Prot4\\resources\\graphs\\final_simple_graph.json",
                    required=False, help="initial graph file path")
parser.add_argument("--fgf", type=str, default="test_graph.json", required=False,
                    help="file name to save the final graph obtained from the simulation")
parser.add_argument("--bom", type=str, default="C:\\Users\\X580\\PycharmProjects\\SP1Prot4\\resources\\BoM.txt",
                    required=False, help="bill of materials file path")
parser.add_argument("--ipp", type=str,
                    default="C:\\Users\\X580\\PycharmProjects\\SP1Prot4\\resources\\initial_poses_roller.txt",
                    required=False, help="initial objects' poses file path")
parser.add_argument("--fpp", type=str,
                    default="C:\\Users\\X580\\PycharmProjects\\SP1Prot4\\resources\\final_poses_roller.txt",
                    required=False, help="final objects' poses file path")
parser.add_argument("--oe", type=int, required=False,
                    help="operator expertise: 0 - beginner, 1 - intermediate, 2 - professional")
parser.add_argument("--am", type=str, default="automatic", required=False,
                    help="automation mode: 'automatic', 'mixed' or 'manual'")
args = parser.parse_args()


def load_graph(graph_file_id_):
    humanid = ids
    if ids is not None:
        os.chdir("C:\\Users\\X580\\PycharmProjects\\SP1Prot4\\resources\\graphs")
        human_id = "*" + humanid + ".json"
        for graph_id in glob.glob(human_id):
            graph_file_id_ = graph_id

    if graph_file_id_ is not None:
        logging.info('LOADING EXISTING GRAPH')
        fgname = "simple_graph_" + humanid + ".json"
        graph = read_json_graph(graph_file_id_)
    else:
        if humanid is None:
            humanid = ""
        logging.info('LOADING NEW GRAPH')
        fgname = "simple_graph_" + humanid + ".json"
        graph = read_json_graph(args.gp)

    if graph is not None:
        final_poses = read_poses(args.fpp)
        if with_nea:
            initial_poses = mqtt.read_mqtt_json(topic_pose)  # nead
        else:
            initial_poses = read_poses(args.ipp)
        operator = Operator(graph, args.oe)
        simulation = Simulation(graph, operator, args.am, initial_poses, final_poses)
        updated_graph, task, simulation_path = simulation.init_simulation()
        log_simulation(task, simulation_path, args.am, updated_graph)
        write_graph_to_file(updated_graph, fgname)
        mqtt.client.publish(topic_request, 'FINISH')


t2 = threading.Thread(target=load_graph, args=(graph_file_id,))
t2.start()
