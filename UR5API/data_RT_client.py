"""
this file allows to parse the data received via Real time client communications interface (port 30003)
data described in Excel document "Client_Interface_V3.5" in the "RealTime_3.2 -> 3.4"" tab
"""

import socket
import time
import struct
import threading
import copy

class dataRT:
    """
    Represents the data received from the Robot UR5 via real-time communications interface
    """

    __slots__ = ['time',
                 'q_target', 'qd_target', 'qdd_target', 'i_target', 'm_target',
                 'q_actual', 'qd_actual', 'i_actual', 'i_control',
                 'tool_vector_actual', 'tcp_speed_actual', 'tcp_force',
                 'tool_vector_target', 'tcp_speed_target',
                 'digital_input_bits', 'motor_temperatures', 'controller_timer',
                 'test_value',
                 'tool_acc_values',
                 'speed_scaling', 'linear_momentum',
                 'v_main', 'v_robot', 'i_robot', 'v_actual', 'digital_outputs', 'program_state']

    def get_data(self):
        """
        Continuously receives data in the buffer and parses it into 31 class __slots__
        """
        host = "192.168.179.128"
        port = 30003
        while True:
            s = socket.create_connection((host, port))
            buf = s.recv(1060)                      # 1060 bytes - size of the total message
            offset = 0
            message_size = struct.unpack_from("!i", buf, offset)[0]
            offset += 4
            if message_size != len(buf):
                print("MessageSize: ", message_size, "; BufferSize: ", len(buf))
                raise Exception("Could not unpack: length field is incorrect")

            rs = dataRT()
            # time: 1double (1x8byte)
            rs.time = struct.unpack_from("!d", buf, offset)[0]
            offset += 8

            # q_target: 6doubles (6x8byte)
            all_values = list(struct.unpack_from("!dddddd", buf, offset))
            offset += 6 * 8
            rs.q_target = copy.deepcopy(all_values)

            # qd_target: 6doubles (6x8byte)
            all_values = list(struct.unpack_from("!dddddd", buf, offset))
            offset += 6 * 8
            rs.qd_target = copy.deepcopy(all_values)

            # qdd_target: 6doubles (6x8byte)
            all_values = list(struct.unpack_from("!dddddd", buf, offset))
            offset += 6 * 8
            rs.qdd_target = copy.deepcopy(all_values)

            # i_target: 6doubles (6x8byte)
            all_values = list(struct.unpack_from("!dddddd", buf, offset))
            offset += 6 * 8
            rs.i_target = copy.deepcopy(all_values)

            # m_target: 6doubles (6x8byte)
            all_values = list(struct.unpack_from("!dddddd", buf, offset))
            offset += 6 * 8
            rs.m_target = copy.deepcopy(all_values)

            # q_actual: 6doubles (6x8byte)
            all_values = list(struct.unpack_from("!dddddd", buf, offset))
            offset += 6 * 8
            rs.q_actual = copy.deepcopy(all_values)

            # qd_actual: 6doubles (6x8byte)
            all_values = list(struct.unpack_from("!dddddd", buf, offset))
            offset += 6 * 8
            rs.qd_actual = copy.deepcopy(all_values)

            # i_actual: 6doubles (6x8byte)
            all_values = list(struct.unpack_from("!dddddd", buf, offset))
            offset += 6 * 8
            rs.i_actual = copy.deepcopy(all_values)

            # i_control: 6doubles (6x8byte)
            all_values = list(struct.unpack_from("!dddddd", buf, offset))
            offset += 6 * 8
            rs.i_control = copy.deepcopy(all_values)

            # tool_vector_actual: 6doubles (6x8byte)
            all_values = list(struct.unpack_from("!dddddd", buf, offset))
            offset += 6 * 8
            rs.tool_vector_actual = copy.deepcopy(all_values)

            # tcp_speed_actual: 6doubles (6x8byte)
            all_values = list(struct.unpack_from("!dddddd", buf, offset))
            offset += 6 * 8
            rs.tcp_speed_actual = copy.deepcopy(all_values)

            # tcp_force: 6doubles (6x8byte)
            all_values = list(struct.unpack_from("!dddddd", buf, offset))
            offset += 6 * 8
            rs.tcp_force = copy.deepcopy(all_values)

            # tool_vector_target: 6doubles (6x8byte)
            all_values = list(struct.unpack_from("!dddddd", buf, offset))
            offset += 6 * 8
            rs.tool_vector_target = copy.deepcopy(all_values)

            # tcp_speed_target: 6doubles (6x8byte)
            all_values = list(struct.unpack_from("!dddddd", buf, offset))
            offset += 6 * 8
            rs.tcp_speed_target = copy.deepcopy(all_values)

            # digital_input_bits: 1double (1x8byte) ?
            rs.digital_input_bits = struct.unpack_from("!d", buf, offset)[0]
            offset += 8

            # motor_temperatures: 6doubles (6x8byte)
            all_values = list(struct.unpack_from("!dddddd", buf, offset))
            offset += 6 * 8
            rs.motor_temperatures = copy.deepcopy(all_values)

            # controller_timer: 1double (1x8byte)
            rs.controller_timer = struct.unpack_from("!d", buf, offset)[0]
            offset += 8

            # test_value: 1double (1x8byte)
            rs.test_value = struct.unpack_from("!d", buf, offset)[0]
            offset += 8

            # robot_mode: 1double (1x8byte)
            rs.robot_mode = struct.unpack_from("!d", buf, offset)[0]
            offset += 8

            # joint_modes: 6double (6x8byte)
            all_values = list(struct.unpack_from("!dddddd", buf, offset))
            offset += 6 * 8
            rs.joint_modes = copy.deepcopy(all_values)

            # safety_mode: 1double (1x8byte)
            rs.safety_mode = struct.unpack_from("!d", buf, offset)[0]
            offset += 8

            # unused: 6double (6x8byte)
            offset += 48

            # tool_acc_values: 3doubles (3x8byte)
            all_values = list(struct.unpack_from("!ddd", buf, offset))
            offset += 3 * 8
            rs.tool_acc_values = copy.deepcopy(all_values)

            # unused: 6doubles (6x8byte)
            offset += 48

            # speed_scaling: 1double (1x8byte)
            rs.speed_scaling = struct.unpack_from("!d", buf, offset)[0]
            offset += 8

            # linear_momentum: 1double (1x8byte)
            rs.linear_momentum = struct.unpack_from("!d", buf, offset)[0]
            offset += 8

            # unused: 2double (2x8bytes)
            offset += 16

            # v_main: 1double (8bytes)
            rs.v_main = struct.unpack_from("!d", buf, offset)[0]
            offset += 8

            # v_robot: 1double (8bytes)
            rs.v_robot = struct.unpack_from("!d", buf, offset)[0]
            offset += 8

            # i_robot: 1double (8bytes)
            rs.i_robot = struct.unpack_from("!d", buf, offset)[0]
            offset += 8

            # v_actual: 6double (6x8byte)
            all_values = list(struct.unpack_from("!dddddd", buf, offset))
            offset += 6 * 8
            rs.v_actual = copy.deepcopy(all_values)

            # digital_output 1double (8bytes)
            rs.digital_outputs = struct.unpack_from("!d", buf, offset)[0]
            offset += 8

            rs.program_state = struct.unpack_from("!d", buf, offset)[0]

            return rs

    def return_value(self, variable):
        """
        variable - string input  with the class __slots__ name (ex: 'time' or 'm_target', according to name in Excel file)
        returns chosen variable value
        """
        rss = dataRT()
        if variable == 'time':
            return rss.get_data().time
        elif variable == 'q_target':
            return rss.get_data().q_target
        elif variable == 'qd_target':
            return rss.get_data().qd_target
        elif variable == 'qdd_target':
            return rss.get_data().qdd_target
        elif variable == 'i_target':
            return rss.get_data().i_target
        elif variable == 'm_target':
            return rss.get_data().m_target
        elif variable == 'q_actual':
            return rss.get_data().q_actual
        elif variable == 'qd_actual':
            return rss.get_data().qd_actual
        elif variable == 'i_actual':
            return rss.get_data().i_actual
        elif variable == 'i_control':
            return self.i_control
        elif variable == 'tool_vector_actual':
            return rss.get_data().tool_vector_actual
        elif variable == 'tcp_speed_actual':
            return rss.get_data().tcp_speed_actual
        elif variable == 'tcp_force':
            return rss.get_data().tcp_force
        elif variable == 'tool_vector_target':
            return rss.get_data().tool_vector_target
        elif variable == 'tcp_speed_target':
            return rss.get_data().tcp_speed_target
        elif variable == 'digital_input_bits':
            return rss.get_data().digital_input_bits
        elif variable == 'motor_temperatures':
            return rss.get_data().motor_temperatures
        elif variable == 'controller_timer':
            return rss.get_data().controller_timer
        elif variable == 'robot_mode':
            return rss.get_data().robot_mode
        elif variable == 'joint_modes':
            return rss.get_data().joint_modes
        elif variable == 'safety_mode':
            return rss.get_data().safety_mode
        elif variable == 'tool_acc_values':
            return rss.get_data().tool_acc_values
        elif variable == 'speed_scaling':
            return rss.get_data().speed_scaling
        elif variable == 'linear_momentum':
            return rss.get_data().linear_momentum
        elif variable == 'v_main':
            return rss.get_data().v_main
        elif variable == 'v_robot':
            return rss.get_data().v_robot
        elif variable == 'i_robot':
            return rss.get_data().i_robot
        elif variable == 'v_actual':
            return rss.get_data().v_actual
        elif variable == 'digital_outputs':
            return rss.get_data().digital_outputs
        elif variable == 'program_state':
            return rss.get_data().program_state
        else:
            raise ValueError("Variable asked to return not defined/valid")

