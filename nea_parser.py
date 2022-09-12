import base64
import numpy as np
from robot.RosBridge import RosBridge
import json
import time
import threading
import random
from math import cos, sin, sqrt, pi

from MQTT_connect import MQQT_client
from utilities.visualizer import Visualizer

socket_ip = "192.168.0.100"  # use external broker
rosport = 9090
rostopic_talk_pose = '/sp1_pose'
rostopic_listen = '/sp1_pose_feedback_detail'
rosmessage_type = 'std_msgs/String'
rostopic_talk_dist = '/sp1_bb'

# MQTT inits
broker_address = 'localhost'  # '192.168.0.9'
broker_port = 1883
topic_human = "DataNea/HumanBB"


class HumanRobotSafety:
    def __init__(self, ros1, mode='none'):
        """Initialize HumanRobotSafety object."""
        self.running_mode = str(mode)  # 'dummy', 'modbus' or 'ur5_api'
        self.human_main = None
        self.arm1 = None
        self.arm2 = None
        self.keypoints = None
        self.mode = mode
        self.mqtt = MQQT_client()
        self.mqtt.new_message.clear()
        self.mqtt.connect(broker_address, broker_port)
        self.mqtt.client.subscribe(topic_human)


        if self.mode == 'ros':
            self.ros_ = ros1
            self.ros_.ros_new_message.clear()

        self.v = Visualizer()

    def pub(self, json_msg):
        while True:
            self.mqtt.client.publish(topic_human, json_msg)
            time.sleep(0.25)

    def get_human(self):
        points = None
        count = 0
        mainbodyq = np.array([[-0.94415569, -0.8301664, 0.93842909], [-0.94415569, -0.6101664, 0.93842909],
                              [-0.94415569, -0.8301664, -0.53208547], [-0.94415569, -0.6101664, -0.53208547],
                              [-0.65473773, -0.8301664, 0.93842909], [-0.65473773, -0.6101664, 0.93842909],
                              [-0.65473773, -0.8301664, -0.53208547], [-0.65473773, -0.6101664, -0.53208547]])
        while True:
            count = count + 1
            mainbody = []
            arm1 = []
            arm2 = []
            obj = self.mqtt.read_mqtt_json(topic_human)
            nr_humans = len(obj["BB"])
            for i in range(nr_humans):
                # human id message payload
                id_human = obj["BB"][0]["id"]
                if id_human >= 0:
                    # get main body BB data and decode it
                    mainbody1 = obj["BB"][0]["BB_mainbody"]
                    mainbody1 = base64.decodebytes(mainbody1.encode('utf-8'))
                    mainbody1 = np.frombuffer(mainbody1, dtype=np.float64).reshape((8, 3))
                    mainbody.append(mainbody1)
                    mainbody = [element + count * 0.2 for element in mainbody]  # delete for real

                    # get arm 1 BB data and decode it
                    array_arm1 = obj["BB"][0]["BB_arm1"]
                    array_arm1 = base64.decodebytes(array_arm1.encode('utf-8'))
                    array_arm1 = np.frombuffer(array_arm1, dtype=np.float64).reshape((8, 3))
                    arm1.append(array_arm1)

                    # get arm 2 BB data and decode it
                    array_arm2 = obj["BB"][0]["BB_arm2"]
                    array_arm2 = base64.decodebytes(array_arm2.encode('utf-8'))
                    array_arm2 = np.frombuffer(array_arm2, dtype=np.float64).reshape((8, 3))
                    arm2.append(array_arm2)

                    # get human joints data and decode it
                    array_keypoints = obj["BB"][0]["3D_keypoints"]
                    array_keypoints = base64.decodebytes(array_keypoints.encode('utf-8'))

                    array_keypoints = np.frombuffer(array_keypoints, dtype=np.float64).reshape((-1, 4))
                    self.keypoints = array_keypoints
                    print(array_keypoints)
            self.human_main = mainbody
            mainbody[0][:, 1] = -1 * mainbody[0][:, 1]
            mainbody[0][:, 0] = -1 * mainbody[0][:, 0]
            # mainbodyq[:, 1]  = mainbodyq[:, 1] + 0.01

            # self.human_main = [mainbodyq]
            
            if self.mode == 'ros':
                print(mainbodyq)
                self.ros_.talk(mainbody, 'dist')

            self.arm1 = arm1
            self.arm2 = arm2
            bb_points, bb_lines = self.plot_util()
            self.v.visualizer3DOpen3d(points, bb_points=bb_points, bb_lines=bb_lines)
            self.v.show()

    def plot_util(self):
        bb_line = np.empty([0, 2])
        bb_points = []
        if self.human_main:
            bb_points = np.vstack(self.human_main)
            for i in range(0, (len(self.human_main))):
                lines_i = np.array([[0, 1], [1, 3], [3, 2], [2, 0], [0, 4], [1, 5], [3, 7], [2, 6], [4, 5], [5, 7],
                                    [7, 6], [6, 4]]) + 8 * i
                bb_line = np.vstack((bb_line, lines_i))
        if self.arm1:
            a1 = np.vstack(self.arm1)
            bb_points = np.vstack((bb_points, a1))
            for i in range(len(self.human_main), len(self.human_main) + 1 + len(self.arm1)):
                lines_i = np.array([[0, 1], [1, 3], [3, 2], [2, 0], [0, 4], [1, 5], [3, 7], [2, 6], [4, 5], [5, 7],
                                    [7, 6], [6, 4]]) + 8 * i
                bb_line = np.vstack((bb_line, lines_i))
        if self.arm2:
            a2 = np.vstack(self.arm2)
            bb_points = np.vstack((bb_points, a2))
            for i in range(len(self.human_main) + 1 + len(self.arm1),
                           len(self.human_main) + 1 + len(self.arm1) + len(self.arm2)):
                lines_i = np.array([[0, 1], [1, 3], [3, 2], [2, 0], [0, 4], [1, 5], [3, 7], [2, 6], [4, 5], [5, 7],
                                    [7, 6], [6, 4]]) + 8 * i
                bb_line = np.vstack((bb_line, lines_i))
        return bb_points, bb_line

'''
ros = RosBridge()
ros.ros_new_message.clear()
ros.connect(socket_ip, rosport, topic_talk_dist=rostopic_talk_dist, topic_talk_pose=rostopic_talk_pose,
            topic_listen=rostopic_listen, message_type=rosmessage_type)
hrc = HumanRobotSafety(ros)
t = threading.Thread(target=hrc.get_human)
t.start()
data_ = json.load(open("data_2.json", "r"))
data = json.dumps(data_)
t1 = threading.Thread(target=hrc.pub, args=(data,))
t1.start()
'''