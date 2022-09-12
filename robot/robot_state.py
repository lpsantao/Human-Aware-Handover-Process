from UR5API.client_api import Client_API
from robot.gripper_mqtt import GripperControl
from robot.RosBridge import RosBridge
from os import path
from pocketsphinx.pocketsphinx import *
import pyaudio
import time
import logging
from queue import Queue
import threading
import nea_parser
import json

logging.basicConfig(level=logging.INFO)
stop = ['stop', 'stopped', 'not']
drop = ['drop', 'drown', 'draw', 'job', 'dot', "drama", "from"]

socket_ip = "192.168.0.100"  # use external broker
rosport = 9090
rostopic_talk_pose = '/sp1_pose'
rostopic_listen = '/sp1_pose_feedback'
rosmessage_type = 'std_msgs/String'
rostopic_talk_dist = '/sp1_bb'

keywordList = ['robot', 'okay']
robot = ['robot', 'robots', 'rabbit', 'romans', "romo"]
left = ['left', 'length', 'lady', 'lifts', 'life', ' live', 'let', 'late', 'legs']
right = ['right', 'rights', 'rats', 'rest', 'read']
go = ['go', 'hello']


def speech_recognizer(qu):
    # Create a decoder with certain model
    MODELDIR = "C:/Users/X580/PycharmProjects/SP1Prot4/pocketsphinx/model"
    DATADIR = "C:/Users/X580/PycharmProjects/SP1Prot4/pocketsphinx/test/data"
    config = Decoder.default_config()
    config.set_string('-logfn', 'nul')
    config.set_string('-hmm', path.join(MODELDIR, 'en-us/en-us'))
    config.set_string('-lm', path.join(MODELDIR, 'en-us/en-us.lm.bin'))
    config.set_string('-dict', path.join(MODELDIR, 'en-us/cmudict-en-us.dict'))
    # Decode streaming data.
    decoder = Decoder(config)
    decoder.start_utt()
    mic = pyaudio.PyAudio()
    in_speech_bf = False

    stream = mic.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024,
                      input_device_index=0)
    stream.start_stream()

    while True:
        buf = stream.read(1024, exception_on_overflow=False)
        if buf:
            qu.queue.clear()
            decoder.process_raw(buf, False, False)
            if decoder.get_in_speech() != in_speech_bf:
                in_speech_bf = decoder.get_in_speech()
                if not in_speech_bf:
                    decoder.end_utt()
                    hypothesis = [seg.word for seg in decoder.seg()]
                    if hypothesis == ['<s>', '[SPEECH]', '</s>'] or hypothesis == ['<s>', '</s>']:
                        decoder.start_utt()
                        continue
                    else:
                        print('Hypothesis result:', decoder.hyp().hypstr)
                        phrase = decoder.hyp().hypstr
                        phrase = phrase.split()
                        qu.put(phrase)
                    decoder.start_utt()
        else:
            break
    decoder.end_utt()


class RobotState:
    def __init__(self, cur_poses, final_poses, graph, flag='robot'):
        # em vez de listas meter as posições como atributos dos nós
        self.cur_poses = cur_poses
        self.final_poses = final_poses
        self.graph = graph
        self.flag = flag
        self.client_api = Client_API()
        self.gripper = GripperControl()
        self.q = Queue()
        self.ros = None
        if self.flag == 'ros':
            self.ros = RosBridge()
            self.ros.ros_new_message.clear()
            self.ros.connect(socket_ip, rosport, topic_talk_dist=rostopic_talk_dist, topic_talk_pose=rostopic_talk_pose,
                             topic_listen=rostopic_listen, message_type=rosmessage_type)
        # t1 = threading.Thread(target=speech_recognizer, args=(self.q,))
        # t1.start()
        self.hrc = nea_parser.HumanRobotSafety(self.ros)
        #data_ = json.load(open("C:/Users/X580/PycharmProjects/SP1Prot4/data_2.json", "r"))
        #data = json.dumps(data_)
        #t2 = threading.Thread(target=self.hrc.pub, args=(data,))
        #t2.start()
        t = threading.Thread(target=self.hrc.get_human)
        t.start()

    def send_move_to_robot(self, node_idx, node_data, simulation_path, time2):

        operation = node_data['operation']
        object_ = node_data['object']
        if operation == 'pick':
            print(self.hrc.keypoints)
            logging.info("going to pick...")
            print(self.cur_poses[object_])
            # move to the current pose of the object
            self.gripper.open_gripper()

            if self.flag == 'ros':
                if self.ros.is_connected():
                    self.cur_poses[object_][2] = self.cur_poses[object_][2] + 0.2
                    self.cur_poses[object_][0] = self.cur_poses[object_][0] * -1
                    self.cur_poses[object_][1] = self.cur_poses[object_][1] * -1
                    self.ros.talk(self.cur_poses[object_], 'pose')
                    print('sent')
                # pos = self.client_api.send_move("movej", self.cur_poses[object_], time2)
                move_done = self.ros.read_ros()
                if move_done == 'goal_ok':
                    print('traj done')
                    self.gripper.close_gripper()
            elif self.flag == 'robot':
                self.cur_poses[object_][2] = self.cur_poses[object_][2] + 0.2
                pos = self.client_api.send_move("movej", self.cur_poses[object_], time2)
                self.cur_poses[object_][2] = self.cur_poses[object_][2] - 0.2
                pos = self.client_api.send_move("movej", self.cur_poses[object_], time2)
                self.gripper.close_gripper()
            else:
                logging.info("empty flag, debug without moving")
        elif operation == 'place':
            logging.info("Placing object...")
            # move object to the object's final pose
            if self.flag == 'ros':
                self.cur_poses[object_][0] = self.cur_poses[object_][0] * -1
                self.cur_poses[object_][1] = self.cur_poses[object_][1] * -1
                self.ros.talk(self.cur_poses[object_], 'pose')
            elif self.flag == 'robot':
                self.client_api.send_move("movej", self.final_poses[object_], time2)
                self.gripper.open_gripper()
            else:
                logging.error("empty flag, debug without moving")
            pos = self.final_poses[object_]
            #word = None
            #while word not in drop:
             #   voice = self.q.get()
             #   for word in voice:
             #       logging.debug("")
            #if word in drop:
              #  logging.info('Dropping the piece!')
                #self.gripper.open_gripper()
        elif operation == 'snap':
            # snap previous object in current object
            previous_node_idx = simulation_path[simulation_path.index(node_idx) - 1]
            previous_node_data = self.graph.nodes.data()[previous_node_idx]
            object_to_snap = previous_node_data['object']
            self.client_api.send_move("movej", self.cur_poses[object_], time2)
            self.cur_poses[object_to_snap] = self.cur_poses[object_]
        elif node_data['operation'] == 'position':
            # move to screw -> place screw in bracket
            self.cur_poses[object_] = self.client_api.send_move("movej", self.cur_poses[object_], time2)

            operations = [node_idx for node_idx in simulation_path if
                          self.graph.nodes.data()[node_idx]['type'] == 'operation']
            previous_node_idx = operations[operations.index(node_idx) - 1]
            previous_node_data = self.graph.nodes.data()[previous_node_idx]
            object_to_place = previous_node_data['object']

            self.client_api.send_move("movej", self.cur_poses[object_to_place], time2)
            self.cur_poses[object_] = self.cur_poses[object_to_place]
