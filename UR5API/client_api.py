import socket
import logging
from threading import Thread, Condition, Lock
from UR5API.data_secondary_client import *


class Client_API:
    def __init__(self):
        self.rs = send_UR()

    def send_move(self, move, pos, time):
        #print(self.rs.get_tcp_pos())
        logging.info('Position %s', pos)
        pos = self.rs.send_move(move, pos)
        return pos

    def stop_mov(self):
        pos = self.rs.stopj()
        return pos
