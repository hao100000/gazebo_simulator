#ifndef GAZEBO_SIMULATOR_CAN_TO_GAZEBO_HPP_
#define GAZEBO_SIMULATOR_CAN_TO_GAZEBO_HPP_

#include <rclcpp/rclcpp.hpp>
#include <std_msgs/msg/float64_multi_array.hpp>
#include <uec_msgs/msg/can_array.hpp>
#include <map>
#include <vector>
#include <string>
#include <yaml-cpp/yaml.h>

// Motor configuration structure
struct MotorConfig {
  uint8_t can_id;
  std::string joint_name;
  bool invert;
  std::string control_type;  // "velocity" or "position"
};

class CanToGazeboNode : public rclcpp::Node {
public:
  CanToGazeboNode();

private:
  void load_motor_config_from_yaml();
  void can_callback(const uec_msgs::msg::CANArray::SharedPtr msg);
  void publish_velocity_command();

  rclcpp::Publisher<std_msgs::msg::Float64MultiArray>::SharedPtr gazebo_pub_;
  rclcpp::Subscription<uec_msgs::msg::CANArray>::SharedPtr can_sub_;

  // Motor configuration from YAML
  std::vector<MotorConfig> motor_configs_;
  
  // CAN ID to joint name mapping
  std::map<uint8_t, std::string> can_id_to_joint_;
  
  // CAN ID to motor index mapping
  std::map<uint8_t, size_t> can_id_to_motor_idx_;
  
  // Joint velocities (ordered by motor config order)
  std::vector<double> joint_velocities_;
};

#endif  // GAZEBO_SIMULATOR_CAN_TO_GAZEBO_HPP_