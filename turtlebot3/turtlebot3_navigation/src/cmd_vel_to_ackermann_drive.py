#!/usr/bin/env python

# Author: christoph.roesmann@tu-dortmund.de
# Modifier: Donghee Han, hdh7485@kaist.ac.kr

import rospy, math
from geometry_msgs.msg import Twist
from ackermann_msgs.msg import AckermannDriveStamped
from ackermann_msgs.msg import AckermannDrive
from std_msgs.msg import String


def convert_trans_rot_vel_to_steering_angle(v, omega, wheelbase):
  if omega == 0 or v == 0:
    return 0

  radius = v / omega
  return math.atan(wheelbase / radius)

def emergency_callback(msg):
  global state
  state = msg.data

def cmd_callback(data):
  global wheelbase
  global ackermann_cmd_topic
  global frame_id
  global pub
  global message_type
  
  v = data.linear.x
  steering = convert_trans_rot_vel_to_steering_angle(v, data.angular.z, wheelbase)

  msg = AckermannDriveStamped()

  if(state != "emergency"):  
    msg.header.stamp = rospy.Time.now()
    msg.header.frame_id = frame_id
    msg.drive.steering_angle = steering
    msg.drive.speed = v
  else: #state == emergency
    msg.header.stamp = rospy.Time.now()
    msg.header.frame_id = frame_id
    msg.drive.steering_angle = 0
    msg.drive.speed = 0
      
  pub.publish(msg)

if __name__ == '__main__': 
  try:
    
    rospy.init_node('cmd_vel_to_ackermann_drive')

    #subscribe 
    twist_cmd_topic = rospy.get_param('~twist_cmd_topic', '/cmd_vel')
    emergency_topic = rospy.get_param('~emergency_topic', '/emergency_state')

    #publish
    ackermann_cmd_topic = rospy.get_param('~ackermann_cmd_topic', '/ackermann_cmd')

    wheelbase = rospy.get_param('~wheelbase', 1.0)
    frame_id = rospy.get_param('~frame_id', 'odom')
    message_type = rospy.get_param('~message_type', 'ackermann_drive') # ackermann_drive or ackermann_drive_stamped

    #subscribe
    rospy.Subscriber(twist_cmd_topic, Twist, cmd_callback, queue_size=1)
    rospy.Subscriber(emergency_topic, String, emergency_callback, queue_size=1)

    #publish
    pub = rospy.Publisher(ackermann_cmd_topic, AckermannDriveStamped, queue_size=1)
    
    rospy.loginfo("Node 'cmd_vel_to_ackermann_drive' started.\nListening to %s, publishing to %s. Frame id: %s, wheelbase: %f", "/cmd_vel", ackermann_cmd_topic, frame_id, wheelbase)
    rospy.spin()
    
  except rospy.ROSInterruptException:
    pass
