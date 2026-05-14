#include "gazebo_simulator/can_to_gazebo.hpp"

CanToGazeboNode::CanToGazeboNode() : rclcpp::Node("can_to_gazebo") {
  // Setup motor to joint name mapping
  motor_to_joint_["wheel_left_joint"] = 1;
  motor_to_joint_["wheel_right_joint"] = 2;

  // Create publisher for velocity commands
  gazebo_pub_ = create_publisher<std_msgs::msg::Float64MultiArray>(
      "/forward_velocity_controller/commands", 10);

  // Create subscription for CAN messages
  can_sub_ = create_subscription<uec_msgs::msg::CANArray>(
      "/can/tx", 10,
      std::bind(&CanToGazeboNode::can_callback, this,
                std::placeholders::_1));

  // Initialize velocities
  joint_velocities_["wheel_left_joint"] = 0.0;
  joint_velocities_["wheel_right_joint"] = 0.0;

  RCLCPP_INFO(get_logger(),
              "CANArray to Gazebo converter initialized. "
              "Listening on /can/tx, publishing to "
              "/forward_velocity_controller/commands");
}

void CanToGazeboNode::can_callback(
    const uec_msgs::msg::CANArray::SharedPtr msg) {
  bool updated = false;

  for (const auto &can_msg : msg->array) {
    uint8_t motor_id = can_msg.bulk_id;
    std::string joint_name;

    // Map motor ID to joint name
    if (motor_id == 1) {
      joint_name = "wheel_left_joint";
    } else if (motor_id == 2) {
      joint_name = "wheel_right_joint";
    } else {
      // Ignore unknown motor IDs
      continue;
    }

    // Extract velocity from CAN data
    double velocity = 0.0;
    if (!can_msg.data.empty()) {
      velocity = static_cast<double>(can_msg.data[0]);
    }

    joint_velocities_[joint_name] = velocity;
    updated = true;

    RCLCPP_DEBUG(get_logger(), "Motor %d (%s) -> velocity: %.2f", motor_id,
                 joint_name.c_str(), velocity);
  }

  if (updated) {
    publish_velocity_command();
  }
}

void CanToGazeboNode::publish_velocity_command() {
  auto msg = std::make_unique<std_msgs::msg::Float64MultiArray>();

  msg->data.push_back(joint_velocities_["wheel_left_joint"]);
  msg->data.push_back(joint_velocities_["wheel_right_joint"]);

  gazebo_pub_->publish(std::move(msg));

  RCLCPP_DEBUG(get_logger(),
               "Published velocities: left=%.2f, right=%.2f",
               joint_velocities_["wheel_left_joint"],
               joint_velocities_["wheel_right_joint"]);
}

int main(int argc, char *argv[]) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<CanToGazeboNode>());
  rclcpp::shutdown();
  return 0;
}
