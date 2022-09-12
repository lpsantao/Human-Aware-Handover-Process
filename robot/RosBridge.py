import roslibpy
import time
import logging
from threading import Event
import numpy as np

'''
def rec_msg(message):
    print('Is operation done?: ' + message['data'])
    global ros_done
    ros_done = message['data']
'''


class RosBridge:

    def __init__(self):
        self.ros_client = None
        self.ros_message = None
        self.talker_dist = None
        self.talker_pose = None
        self.listener = None
        self.status = None
        self.stop = Event()
        self.stop.clear()
        self.ros_new_message = Event()
        self.ros_new_message.clear()

    def connect(self, websocket_ip, port, topic_talk_dist=None, topic_talk_pose=None, topic_listen=None,
                message_type='std_msgs/String'):
        ros_address = 'ws://' + str(websocket_ip) + ':' + str(port)
        logging.info(f"trying to connect to ROS {str(ros_address)}")
        self.ros_client = roslibpy.Ros(host=websocket_ip, port=port)

        def rec_msg(message):
            self.ros_message = message
            self.ros_new_message.set()

        self.ros_client.run()
        if topic_talk_dist is not None:
            self.talker_dist = roslibpy.Topic(self.ros_client, topic_talk_dist, message_type)
        if topic_talk_pose is not None:
            self.talker_pose = roslibpy.Topic(self.ros_client, topic_talk_pose, message_type)
        if topic_listen is not None:
            self.listener = roslibpy.Topic(self.ros_client, topic_listen, message_type)
            self.listener.subscribe(rec_msg)

        self.status = self.is_connected()

    def read_ros(self):
        if self.status is None:
            logging.error('Not connected to ROS server')
        while not self.stop.is_set():
            print('here')
            self.ros_new_message.wait()
            # checks if is the right topic
            if self.ros_message is not None:
                # process each message
                msg = self.ros_message['data']
                self.ros_new_message.clear()
                return msg

    def disconnect(self):
        logging.info(f"trying to disconnect from to ROS")
        self.ros_client.close()
        # self.ros.terminate()
        self.status = self.is_connected()

    def is_connected(self):
        """
        Check connectivity of ROS bridge.
        """
        status = self.ros_client.is_connected
        time.sleep(0.2)
        if status:
            logging.info("ROS Bridge is connected")
        else:
            logging.error("ROS Connectivity Failed")
        return status

    def talk(self, data, topic):
        if topic == 'pose':
            self.talker_pose.publish(roslibpy.Message({'data': str(data)}))
            logging.info('Sending message to ROS: {}'.format(data))
        elif topic == 'dist':
            self.talker_dist.publish(roslibpy.Message({'data': str(data)}))
            logging.info('Sending message to ROS: {}'.format(data))

    def __del__(self):
        self.stop.set()
        self.ros_new_message.clear()
        self.ros_client.terminate()


socket_ip = "192.168.0.100"  # use external broker
rosport = 9090
rostopic_talk_pose = '/sp1_pose'
rostopic_listen = '/sp1_pose_feedback_detail'
rosmessage_type = 'std_msgs/Int32'
rostopic_talk_dist = '/sp1_bb'
