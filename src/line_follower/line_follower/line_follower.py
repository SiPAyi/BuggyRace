import rclpy
from rclpy.node import Node

import math

from synapse_msgs.msg import EdgeVectors

from geometry_msgs.msg import Twist


QOS_PROFILE_DEFAULT = 10

PI = math.pi

LEFT_TURN = +1.0
RIGHT_TURN = -1.0

TURN_MIN = 0.0
TURN_MAX = 1.0
SPEED_MIN = 0.4
SPEED_MAX = 4.0
SPEED_25_PERCENT = SPEED_MAX / 4
SPEED_50_PERCENT = SPEED_25_PERCENT * 2
SPEED_75_PERCENT = SPEED_25_PERCENT * 3


class LineFollower(Node):
	""" Initializes line follower node with the required publishers and subscriptions.

		Returns:
			None
	"""
	def __init__(self):
		super().__init__('line_follower')

		# Subscription for edge vectors.
		self.subscription_vectors = self.create_subscription(
			EdgeVectors,
			'/edge_vectors',
			self.edge_vectors_callback,
			QOS_PROFILE_DEFAULT)

		# Publisher for joy (for moving the rover in manual mode).
		self.publisher_cmd_vel = self.create_publisher(
			Twist,
			'/cmd_vel',
			QOS_PROFILE_DEFAULT)
  
	""" Operates the rover in manual mode by publishing on /cerebri/in/joy.

		Args:
			speed: the speed of the car in float. Range = [-1.0, +1.0];
				Direction: forward for positive, reverse for negative.
			turn: steer value of the car in float. Range = [-1.0, +1.0];
				Direction: left turn for positive, right turn for negative.

		Returns:
			None
	"""
	def buggy_move(self, speed, turn):
		msg = Twist()
		msg.linear.x = speed
		msg.angular.z = turn
		self.publisher_cmd_vel.publish(msg)

	""" Analyzes edge vectors received from /edge_vectors to achieve line follower application.
		It checks for existence of ramps & obstacles on the track through instance members.
			These instance members are updated by the lidar_callback using LIDAR data.
		The speed and turn are calculated to move the rover using buggy_move.

		Args:
			message: "~/cognipilot/cranium/src/synapse_msgs/msg/EdgeVectors.msg"

		Returns:
			None
	"""
	def edge_vectors_callback(self, message):
		vectors = message
		half_width = vectors.image_width / 2
		turn = 0.0

		# NOTE: participants may improve algorithm for line follower.
		if (vectors.vector_count == 0):  # none.
			pass

		if (vectors.vector_count == 1): 
			x_mid = (vectors.vector_1[1].x + vectors.vector_1[0].x)/2
			deviation = (half_width - x_mid)/half_width
			turn = deviation

		if (vectors.vector_count == 2): 
			pass

		self.buggy_move(SPEED_MAX, turn)
        


def main(args=None):
	rclpy.init(args=args)

	line_follower = LineFollower()

	rclpy.spin(line_follower)

	# Destroy the node explicitly
	# (optional - otherwise it will be done automatically
	# when the garbage collector destroys the node object)
	line_follower.destroy_node()
	rclpy.shutdown()


if __name__ == '__main__':
	main()