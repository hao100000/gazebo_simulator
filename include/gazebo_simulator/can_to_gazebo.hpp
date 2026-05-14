#ifndef GAZEBO_SIMULATOR_CAN_TO_GAZEBO_HPP_
#define GAZEBO_SIMULATOR_CAN_TO_GAZEBO_HPP_

#include <rclcpp/rclcpp.hpp>
#include <std_msgs/msg/float64_multi_array.hpp>
#include <uec_msgs/msg/can_array.hpp>
#include <map>
#include <vector>

class CanToGazeboNode : public rclcpp::Node {
public:
  CanToGazeboNode();

private:
  void can_callback(const uec_msgs::msg::CANArray::SharedPtr msg);
  void publish_velocity_command();

  rclcpp::Publisher<std_msgs::msg::Float64MultiArray>::SharedPtr gazebo_pub_;
  rclcpp::Subscription<uec_msgs::msg::CANArray>::SharedPtr can_sub_;

  std::map<std::string, uint8_t> motor_to_joint_;
  std::map<std::string, double> joint_velocities_;
};

#endif  // GAZEBO_SIMULATOR_CAN_TO_GAZEBO_HPP_