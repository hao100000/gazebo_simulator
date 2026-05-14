#include <rclcpp/rclcpp.hpp>
#include <trajectory_msgs/msg/joint_trajectory.hpp>
#include <trajectory_msgs/msg/joint_trajectory_point.hpp>
#include <uec_msgs/msg/can_array.hpp>
#include <map>
#include <vector>

class CanToJointTrajectoryNode : public rclcpp::Node {
public:
  CanToJointTrajectoryNode() : Node("can_to_joint_trajectory") {
    // Setup motor to joint name mapping
    motor_to_joint_["wheel_left_joint"] = 1;
    motor_to_joint_["wheel_right_joint"] = 2;

    // Create publisher for joint trajectory commands
    joint_trajectory_pub_ =
        create_publisher<trajectory_msgs::msg::JointTrajectory>(
            "/demorobot_joint_trajectory_controller/commands", 10);

    // Create subscription for CAN messages
    can_sub_ = create_subscription<uec_msgs::msg::CANArray>(
        "/can/tx", 10,
        std::bind(&CanToJointTrajectoryNode::can_callback, this,
                  std::placeholders::_1));

    // Initialize velocities
    joint_velocities_["wheel_left_joint"] = 0.0;
    joint_velocities_["wheel_right_joint"] = 0.0;

    RCLCPP_INFO(get_logger(),
                "CANArray to JointTrajectory converter initialized. "
                "Listening on /can/tx");
  }

private:
  void can_callback(const uec_msgs::msg::CANArray::SharedPtr msg) {
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
      publish_joint_trajectory();
    }
  }

  void publish_joint_trajectory() {
    auto trajectory_msg = std::make_shared<trajectory_msgs::msg::JointTrajectory>();

    trajectory_msg->header.stamp = now();
    trajectory_msg->header.frame_id = "";

    // Set joint names
    trajectory_msg->joint_names = {"wheel_left_joint", "wheel_right_joint"};

    // Create a single trajectory point with current velocities
    trajectory_msgs::msg::JointTrajectoryPoint point;
    point.velocities.push_back(joint_velocities_["wheel_left_joint"]);
    point.velocities.push_back(joint_velocities_["wheel_right_joint"]);

    // Set time from start (use small value for immediate execution)
    point.time_from_start.sec = 0;
    point.time_from_start.nanosec = 100000000; // 0.1 seconds

    trajectory_msg->points.push_back(point);

    joint_trajectory_pub_->publish(*trajectory_msg);

    RCLCPP_DEBUG(get_logger(), "Published joint trajectory: left=%.2f, right=%.2f",
                 joint_velocities_["wheel_left_joint"],
                 joint_velocities_["wheel_right_joint"]);
  }

  rclcpp::Publisher<trajectory_msgs::msg::JointTrajectory>::SharedPtr
      joint_trajectory_pub_;
  rclcpp::Subscription<uec_msgs::msg::CANArray>::SharedPtr can_sub_;

  std::map<std::string, uint8_t> motor_to_joint_;
  std::map<std::string, double> joint_velocities_;
};

int main(int argc, char *argv[]) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<CanToJointTrajectoryNode>());
  rclcpp::shutdown();
  return 0;
}
