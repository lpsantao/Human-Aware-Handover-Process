import paho.mqtt.client as mqtt
import time


class GripperControl:
    def __init__(self):
        self.broker_address = "192.168.0.10"  # use external broker

        self.client = mqtt.Client()  # create new instance
        self.client.on_message = self.on_message
        self.client.connect(self.broker_address, port=1883)  # connect to broker
        self.client.loop_start()

    def on_message(self, client, userdata, message):
        print("message received ", str(message.payload.decode("utf-8")))
        print("message topic=", message.topic)
        print("message qos=", message.qos)
        print("message retain flag=", message.retain)

    def close_gripper(self):
        self.client.publish("topic/gripper", '{0}'.format(100))

    def open_gripper(self):
        self.client.publish("topic/gripper", '{0}'.format(0))

    def __del__(self):
        self.client.disconnect()
        self.client.loop_stop()


'''
gp = GripperControl()
gp.open_gripper()
time.sleep(1)
gp.close_gripper()
time.sleep(1)
gp.open_gripper()
time.sleep(1)
gp.close_gripper()
time.sleep(1)
'''