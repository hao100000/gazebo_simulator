#!/usr/bin/env python3

"""Convert /can/tx motor commands into Gazebo joint velocity commands.

Motor 1 drives the left wheel joint and motor 2 drives the right wheel joint.
Other motor IDs are ignored for now.
"""

import rclpy
from rclpy.node import Node

from std_msgs.msg import Float64
from uec_msgs.msg import CANArray


class CanToJointVelocityNode(Node):
    def __init__(self) -> None:
        super().__init__('can_to_joint_velocity')

        self._motor_to_joint_topic = {
            1: '/model/demoRobot/joint/wheel_left_joint/cmd_vel',
            2: '/model/demoRobot/joint/wheel_right_joint/cmd_vel',
        }
        self._current_velocity_by_motor = {1: 0.0, 2: 0.0}

        self._publishers = {
            motor_id: self.create_publisher(Float64, topic, 10)
            for motor_id, topic in self._motor_to_joint_topic.items()
        }

        self.create_subscription(CANArray, '/can/tx', self._on_can_array, 10)

        self.get_logger().info(
            'Listening on /can/tx and forwarding motor 1/2 to wheel joints.'
        )

    def _on_can_array(self, message: CANArray) -> None:
        updated = False

        for can_message in message.array:
            motor_id = int(can_message.bulk_id)
            if motor_id not in self._current_velocity_by_motor:
                continue

            target_velocity = 0.0
            if can_message.data:
                target_velocity = float(can_message.data[0])

            self._current_velocity_by_motor[motor_id] = target_velocity
            updated = True

        if updated:
            self._publish_current_commands()

    def _publish_current_commands(self) -> None:
        for motor_id, publisher in self._publishers.items():
            command = Float64()
            command.data = self._current_velocity_by_motor[motor_id]
            publisher.publish(command)

    def stop_all(self) -> None:
        for motor_id in self._current_velocity_by_motor:
            self._current_velocity_by_motor[motor_id] = 0.0
        self._publish_current_commands()


def main() -> None:
    rclpy.init()
    node = CanToJointVelocityNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.stop_all()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()