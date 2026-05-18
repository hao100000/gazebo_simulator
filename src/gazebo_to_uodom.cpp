#include <cmath>
#include <memory>
#include <string>

#include <rclcpp/rclcpp.hpp>
#include <tf2_msgs/msg/tf_message.hpp>
#include <uec_msgs/msg/odometry.hpp>

class GazeboToUodomNode : public rclcpp::Node {
public:
  GazeboToUodomNode()
  : rclcpp::Node("gazebo_to_uodom")
  {
    input_topic_ = declare_parameter<std::string>("input_topic", "/model/omni_robot/pose");
    output_topic_ = declare_parameter<std::string>("output_topic", "/uodom");
    target_child_frame_id_ = declare_parameter<std::string>("target_child_frame_id", "omni_robot");

    publisher_ = create_publisher<uec_msgs::msg::Odometry>(output_topic_, 10);
    subscription_ = create_subscription<tf2_msgs::msg::TFMessage>(
      input_topic_, 10,
      std::bind(&GazeboToUodomNode::tf_callback, this, std::placeholders::_1));

    RCLCPP_INFO(
      get_logger(),
      "Listening on %s and publishing robot body pose to %s for child_frame_id='%s'",
      input_topic_.c_str(), output_topic_.c_str(), target_child_frame_id_.c_str());
  }

private:
  void tf_callback(const tf2_msgs::msg::TFMessage::SharedPtr msg)
  {
    for (const auto & transform : msg->transforms) {
      if (transform.child_frame_id != target_child_frame_id_) {
        continue;
      }

      const auto & q = transform.transform.rotation;
      const double siny_cosp = 2.0 * (q.w * q.z + q.x * q.y);
      const double cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z);

      uec_msgs::msg::Odometry odom;
      odom.x = static_cast<float>(transform.transform.translation.x);
      odom.y = static_cast<float>(transform.transform.translation.y);
      odom.yaw = static_cast<float>(std::atan2(siny_cosp, cosy_cosp));
      odom.vx = 0.0f;
      odom.vy = 0.0f;
      odom.vyaw = 0.0f;

      publisher_->publish(odom);
      RCLCPP_DEBUG(
        get_logger(),
        "Published body pose: frame_id='%s' child_frame_id='%s'",
        transform.header.frame_id.c_str(), transform.child_frame_id.c_str());
      return;
    }
  }

  std::string input_topic_;
  std::string output_topic_;
  std::string target_child_frame_id_;
  rclcpp::Publisher<uec_msgs::msg::Odometry>::SharedPtr publisher_;
  rclcpp::Subscription<tf2_msgs::msg::TFMessage>::SharedPtr subscription_;
};

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<GazeboToUodomNode>());
  rclcpp::shutdown();
  return 0;
}
