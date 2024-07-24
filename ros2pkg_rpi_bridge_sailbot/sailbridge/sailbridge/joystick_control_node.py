'''
 Developed in Researchlab Autonomous Shipping (RAS) Delft
 Department Maritime and Transport Technology of faculty 3mE, TU Delft. 
 https://rasdelft.nl/nl/

 Bart Boogmans
 bartboogmans@hotmail.com
'''
import signal
from re import T
import sys
from rclpy.node import Node
import rclpy
import os 
import pygame

import numpy as np
from rclpy.qos import QoSProfile
from rclpy.qos import QoSReliabilityPolicy, QoSHistoryPolicy, QoSDurabilityPolicy

# import float32 msg
from std_msgs.msg import Float32
import os
from ament_index_python.packages import get_package_share_directory

import ras_ros_core_control_modules.tools.titoneri_parameters as titoneri_parameters
from joystick_control_ras.plot_tools import plotColorPalette, plotTree2d, make_arrow
from joystick_control_ras.allocation_functions import joy2act_TN_01
from sensor_msgs.msg import JointState

def joy2act_TN_01(joy: pygame.joystick.Joystick):


    ax_speed = (-joy.get_axis(3))/2.0 +0.5

    if ax_speed > 0.05:
        speed = ax_speed
    else:
        speed = -joy.get_axis(1)

    # if abs(speed) <0.02: set to zero
    if abs(speed) < 0.02:
        speed = 0.0
        
    speed_TN_aft_max = 3000
    rotation_azi_TN_set_max = (1/3)*3.14159
    bow_TN_set_max = 0.3

    return [    speed_TN_aft_max*speed, 
                speed_TN_aft_max*speed,
                (joy.get_button(3)-joy.get_button(2))*bow_TN_set_max*(1+joy.get_button(0)),
                -rotation_azi_TN_set_max*joy.get_axis(0), 
                -rotation_azi_TN_set_max*joy.get_axis(0)]


class JoystickSailboatNode(Node):
    """ Manages ROS2 communication."""

    def __init__(self):
        super().__init__('sailboat_joystick_node')

    
        custom_qos_profile = QoSProfile(
    		reliability=QoSReliabilityPolicy.BEST_EFFORT,
    		history=QoSHistoryPolicy.KEEP_LAST,
    		depth=1,
    		durability=QoSDurabilityPolicy.VOLATILE
		)
        self.declare_parameter('publish_rate', 10.0) # Hz
        self.declare_parameter('joystick_nr', 0) # to indicate which joystick to use in case of multiple joysticks
        self.declare_parameter('rudder_angle_max_abs', 30.0) # degrees
        self.declare_parameter('rudder_angle_offset', 5.0) # degrees
        self.declare_parameter('sail_angle_max', 90.0) # degrees
        self.declare_parameter('gain_rudder', 45) # degrees / axis value
        
        # Initialize the joystick
        pygame.init()
        pygame.joystick.init()
        self.joystick = pygame.joystick.Joystick(self.get_parameter('joystick_nr').value)
        self.joystick.init()
        
        self.pub_actuation = self.create_publisher(JointState, 'actuation', custom_qos_profile)
        self.timer_actuation = self.create_timer(1.0/self.get_parameter('publish_rate').value,self.timer_callback_publish_actuation)
    
    # Destructor
    def __del__(self):
        if self.joystick != None:
            self.joystick.quit()
            self.joystick = None

    def timer_callback_publish_actuation(self):
        pygame.event.pump()
        ax_sail = (-self.joystick.get_axis(3))/2.0 +0.5 # 0.0 to 1.0
        ax_rudder = self.joystick.get_axis(0) # -1.0 to 1.0

        ## Map sail joystick value (0-1)to sail servo angle (-90 to 90)
        sail_angle = ax_sail * 180 - 90.0

        ## Map rudder joystick value (-1 to 1) to rudder servo angle (-45 to 45)
        rudder_angle = ax_rudder * self.get_parameter('gain_rudder').value

        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = ['rudder_angle', 'sail_angle']
        msg.position = [rudder_angle + self.get_parameter('rudder_angle_offset').value, sail_angle]
        msg.velocity = []
        msg.effort = []
        
        ## Print what we are publishing
        self.get_logger().info(f'Publishing actuation: rudder_angle: {rudder_angle}, sail_angle: {sail_angle}')

        self.pub_actuation.publish(msg)

        
    def read_joystick(self):
        """
        Updates the sliders to the joystick values.
        """
        if self.joystick != None:
            pygame.event.pump()
            joystick_values = joy2act_TN_01(self.joystick)
            
            # Set the sliders to the joystick values
            self.slider_rpm_SB.setValue(int(joystick_values[0]))
            self.slider_rpm_PS.setValue(int(joystick_values[1]))

            self.slider_bow.setValue(int(joystick_values[2]*100.0))

            # The joystick values are in radians, but the sliders are in degrees
            self.slider_angle_SB.setValue(int(np.degrees(joystick_values[3])))
            self.slider_angle_PS.setValue(int(np.degrees(joystick_values[4])))
    
     
def main(args=None):
    rclpy.init(args=args)
    node = JoystickSailboatNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()