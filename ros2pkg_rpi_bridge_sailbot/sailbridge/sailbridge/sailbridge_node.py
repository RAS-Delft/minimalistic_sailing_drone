import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from time import time
from rclpy.qos import QoSProfile
from rclpy.qos import QoSReliabilityPolicy, QoSHistoryPolicy, QoSDurabilityPolicy

class SailbridgeNode(Node):
    def __init__(self):
        super().__init__('sailbridge_node')
        self.sail_angle = 0.0
        self.rudder_angle = 0.0
        self.last_actuation_time = 0
        self.actuation_count = 0

        custom_qos_profile = QoSProfile(
    		reliability=QoSReliabilityPolicy.BEST_EFFORT,
    		history=QoSHistoryPolicy.KEEP_LAST,
    		depth=1,
    		durability=QoSDurabilityPolicy.VOLATILE
		)

        self.actuation_sub = self.create_subscription(
            JointState,'actuation',self.actuation_callback,custom_qos_profile)

        self.timer = self.create_timer(5.0, self.report_status)

    def actuation_callback(self, msg: JointState):
        current_time = time()
        if current_time - self.last_actuation_time >= 0.05:
            self.rudder_angle = msg.position[0]
            self.sail_angle = msg.position[1]

            self.last_actuation_time = current_time
            self.actuation_count += 1


    def report_status(self):
        self.get_logger().info(f'Total sail messages received: {self.actuation_count}')
        self.get_logger().info(f'Current sail angle: {self.sail_angle}')
        self.get_logger().info(f'Current rudder angle: {self.rudder_angle}')

        # reset counters
        self.actuation_count = 0

def main(args=None):
    rclpy.init(args=args)
    node = SailbridgeNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()