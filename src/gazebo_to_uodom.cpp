#include <cmath>
#include <memory>
#include <string>

#include <geometry_msgs/msg/transform_stamped.hpp>
#include <nav_msgs/msg/odometry.hpp>
#include <rclcpp/rclcpp.hpp>
#include <tf2_msgs/msg/tf_message.hpp>
#include <tf2_ros/transform_broadcaster.h>
#include <uec_msgs/msg/odometry.hpp>

class GazeboToUodomNode : public rclcpp::Node {
public:
  GazeboToUodomNode()
  : rclcpp::Node("gazebo_to_uodom")
  {
    input_topic_ = declare_parameter<std::string>("input_topic", "/model/omni_robot/pose");
    output_topic_ = declare_parameter<std::string>("output_topic", "/uodom");
    target_child_frame_id_ = declare_parameter<std::string>("target_child_frame_id", "omni_robot");
    odom_topic_ = declare_parameter<std::string>("odom_topic", "/odom");
    odom_frame_id_ = declare_parameter<std::string>("odom_frame_id", "odom");
    base_frame_id_ = declare_parameter<std::string>("base_frame_id", "base_link");
    publish_odom_ = declare_parameter<bool>("publish_odom", true);
    publish_tf_ = declare_parameter<bool>("publish_tf", true);

    uodom_pub_ = create_publisher<uec_msgs::msg::Odometry>(output_topic_, 10);
    if (publish_odom_) {
      odom_pub_ = create_publisher<nav_msgs::msg::Odometry>(odom_topic_, 10);
    }
    if (publish_tf_) {
      tf_broadcaster_ = std::make_unique<tf2_ros::TransformBroadcaster>(*this);
    }
    subscription_ = create_subscription<tf2_msgs::msg::TFMessage>(
      input_topic_, 10,
      std::bind(&GazeboToUodomNode::tf_callback, this, std::placeholders::_1));

    RCLCPP_INFO(
      get_logger(),
      "Listening on %s and publishing %s plus %s/%s TF for child_frame_id='%s'",
      input_topic_.c_str(), output_topic_.c_str(), odom_frame_id_.c_str(),
      base_frame_id_.c_str(), target_child_frame_id_.c_str());
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

      uodom_pub_->publish(odom);

      if (publish_odom_ && odom_pub_) {
        nav_msgs::msg::Odometry nav_odom;
        nav_odom.header.stamp = transform.header.stamp;
        nav_odom.header.frame_id = odom_frame_id_;
        nav_odom.child_frame_id = base_frame_id_;
        nav_odom.pose.pose.position.x = transform.transform.translation.x;
        nav_odom.pose.pose.position.y = transform.transform.translation.y;
        nav_odom.pose.pose.position.z = transform.transform.translation.z;
        nav_odom.pose.pose.orientation = transform.transform.rotation;
        odom_pub_->publish(nav_odom);
      }

      if (publish_tf_ && tf_broadcaster_) {
        geometry_msgs::msg::TransformStamped odom_tf;
        odom_tf.header.stamp = transform.header.stamp;
        odom_tf.header.frame_id = odom_frame_id_;
        odom_tf.child_frame_id = base_frame_id_;
        odom_tf.transform = transform.transform;
        tf_broadcaster_->sendTransform(odom_tf);
      }

      RCLCPP_DEBUG(
        get_logger(),
        "Published body pose: frame_id='%s' child_frame_id='%s'",
        transform.header.frame_id.c_str(), transform.child_frame_id.c_str());
      return;
    }
  }

  std::string input_topic_;
  std::string output_topic_;
  std::string odom_topic_;
  std::string target_child_frame_id_;
  std::string odom_frame_id_;
  std::string base_frame_id_;
  bool publish_odom_;
  bool publish_tf_;
  rclcpp::Publisher<uec_msgs::msg::Odometry>::SharedPtr uodom_pub_;
  rclcpp::Publisher<nav_msgs::msg::Odometry>::SharedPtr odom_pub_;
  rclcpp::Subscription<tf2_msgs::msg::TFMessage>::SharedPtr subscription_;
  std::unique_ptr<tf2_ros::TransformBroadcaster> tf_broadcaster_;
};

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<GazeboToUodomNode>());
  rclcpp::shutdown();
  return 0;
}
