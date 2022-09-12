from threading import Event, Thread
from paho.mqtt.client import Client
import random
import numpy as np
import base64
import json
import time


class MQQT_client:
    def __init__(self):
        self.client = None
        self.topic = None
        self.message = None
        self.new_message = Event()
        self.stop = Event()
        self.new_message.clear()
        self.client_id = f'python-mqtt-{random.randint(0, 1000)}'

    def connect(self, host, port):
        self.client = Client(self.client_id)

        def on_connect(client, userdata, flags, rc):
            print("Connected With Client ID: {}".format(self.client_id))

        def on_message(client, userdata, message):
            # print('new message from: {}'.format(message.topic))
            self.topic = message.topic
            self.message = message.payload
            self.new_message.set()

        self.client.on_connect = on_connect
        self.client.on_message = on_message
        self.client.connect(host, port)
        self.client.loop_start()

    def read_mqtt(self, topic):
        while not self.stop.is_set():
            self.new_message.wait()
            # checks if is the right topic
            if self.topic == topic and self.message is not None:
                # process each message
                msg = self.message.decode('utf-8')
                self.new_message.clear()
                return msg

    def read_mqtt_json(self, topic):
        while not self.stop.is_set():
            self.new_message.wait()           ### UNCOMMENT FOR REAL TESTS
            # checks if is the right topic
            #print('mes:',self.message)
            if self.topic == topic and self.message is not None:
                # process each message
                msg = json.loads(self.message)
                self.new_message.clear()
                return msg

    def __del__(self):
        self.stop.set()
        self.new_message.clear()
        self.client.disconnect()

'''
def read_value():
    obj = mqtt.read_mqtt(topic)
    print(obj)

def pub(json_msg):
        mqtt.client.publish(topic, (json_msg))
        time.sleep(1)

#data1 = json.load(open("data_all.json","r"))

data = 'hello'#json.dumps(data1)
broker_address = "localhost"  # use external broker
broker_port = 1883
topic = "topic/ubi/pose"
mqtt = MQQT_client()
mqtt.new_message.clear()
mqtt.connect(broker_address, broker_port)
mqtt.client.subscribe(topic)


t2 = Thread(target=pub, args=(data,))
t = Thread(target=read_value)

t2.start()
t.start()
'''