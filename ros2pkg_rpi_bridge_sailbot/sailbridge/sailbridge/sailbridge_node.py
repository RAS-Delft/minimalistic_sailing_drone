import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from time import time
from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy, QoSDurabilityPolicy
import RPi.GPIO as GPIO

class SailbridgeNode(Node):
    def __init__(self):
        super().__init__('sailbridge_node')
        self.sail_angle = 0.0
        self.rudder_angle = 0.0
        self.last_actuation_time = 0
        self.actuation_count = 0

        # GPIO setup
        GPIO.setwarnings(False) # Suppress warnings for GPIO allocation.
        GPIO.setmode(GPIO.BCM)
        self.rudder_pin = 14
        self.sail_pin = 15
        GPIO.setup(self.rudder_pin, GPIO.OUT)
        GPIO.setup(self.sail_pin, GPIO.OUT)

        # Initialize PWM on the GPIO pins
        self.rudder_servo = GPIO.PWM(self.rudder_pin, 50)  # 50Hz PWM frequency
        self.sail_servo = GPIO.PWM(self.sail_pin, 50)
        self.rudder_servo.start(0)
        self.sail_servo.start(0)

        custom_qos_profile = QoSProfile(
            reliability=QoSReliabilityPolicy.BEST_EFFORT,
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=1,
            durability=QoSDurabilityPolicy.VOLATILE
        )

        self.actuation_sub = self.create_subscription(
            JointState,
            'actuation',
            self.actuation_callback,
            custom_qos_profile
        )

        self.timer = self.create_timer(5.0, self.report_status)

    def angle_to_duty_cycle(self, angle):
        # Convert angle (0-180) to duty cycle (2-12)
        cycle = 2 + (angle / 180.0) * 10
        # limit from 0 to 100
        if cycle >100:
            return 100
        elif cycle <0:
            return 0
        else:
            return cycle
        
    def actuation_callback(self, msg: JointState):
        current_time = time()
        if current_time - self.last_actuation_time >= 0.05:
            self.rudder_angle = msg.position[0]
            self.sail_angle = msg.position[1]

            self.last_actuation_time = current_time
            self.actuation_count += 1

            print(f'Actuation received: rudder_angle: {self.rudder_angle}, sail_angle: {self.sail_angle}')
            # Control servos
            rudder_duty_cycle = self.angle_to_duty_cycle(self.rudder_angle+90.0)
            sail_duty_cycle = self.angle_to_duty_cycle(self.sail_angle*2.0)
            print(f'Rudder: {rudder_duty_cycle}, Sail: {sail_duty_cycle}')

            self.rudder_servo.ChangeDutyCycle(rudder_duty_cycle)
            self.sail_servo.ChangeDutyCycle(sail_duty_cycle)

    def report_status(self):
        self.get_logger().info(f'Total sail messages received: {self.actuation_count}')
        self.get_logger().info(f'Current sail angle: {self.sail_angle}')
        self.get_logger().info(f'Current rudder angle: {self.rudder_angle}')
        self.actuation_count = 0

    def destroy_node(self):
        # Cleanup GPIO
        self.rudder_servo.stop()
        self.sail_servo.stop()
        GPIO.cleanup()
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    node = SailbridgeNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()