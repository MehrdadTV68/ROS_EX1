#! /usr/bin/env python

import rospy
from geometry_msgs.msg import Twist, Point
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry
from tf import transformations
from std_srvs.srv import *

import math

pub = None
srv_client_go_to_point_ = None
srv_client_wall_follower_ = None
srv_client_user_interface_ = None
srv_client_random_position_ = None
yaw_ = 0
yaw_error_allowed_ = 5 * (math.pi / 180)  # 5 degrees
position_ = Point()
desired_position_ = Point()
desired_position_.x = rospy.get_param('des_pos_x')
desired_position_.y = rospy.get_param('des_pos_y')
desired_position_.z = 0
regions_ = None
state_desc_ = ['Go to point', 'wall following', 'target reached', 'user control']
state_ = 3

# callbacks
def clbk_odom(msg):
    global position_, yaw_

    # position
    position_ = msg.pose.pose.position

    # yaw
    quaternion = (
        msg.pose.pose.orientation.x,
        msg.pose.pose.orientation.y,
        msg.pose.pose.orientation.z,
        msg.pose.pose.orientation.w)
    euler = transformations.euler_from_quaternion(quaternion)
    yaw_ = euler[2]


def clbk_laser(msg):
    global regions_
    regions_ = {
        'right':  min(min(msg.ranges[0:143]), 10),
        'fright': min(min(msg.ranges[144:287]), 10),
        'front':  min(min(msg.ranges[288:431]), 10),
        'fleft':  min(min(msg.ranges[432:575]), 10),
        'left':   min(min(msg.ranges[576:719]), 10),
    }


def change_state(state):
    global state_, state_desc_
    global srv_client_wall_follower_, srv_client_go_to_point_, srv_client_user_interface_
    state_ = state
    log = "BUG.py:: state changed: %s" % state_desc_[state]
    print(log)
    if state_ == 0:
        resp = srv_client_go_to_point_(True)
        resp = srv_client_wall_follower_(False)
        resp = srv_client_user_interface_(False)
    elif state_ == 1:
        resp = srv_client_go_to_point_(False)
        resp = srv_client_wall_follower_(True)
        resp = srv_client_user_interface_(False)
    elif state_ == 2:
        resp = srv_client_go_to_point_(False)
        resp = srv_client_wall_follower_(False)
        resp = srv_client_user_interface_(True)
        
        twist_msg = Twist()
        twist_msg.linear.x = 0
        twist_msg.angular.z = 0
        pub.publish(twist_msg)

def normalize_angle(angle):
    if(math.fabs(angle) > math.pi):
        angle = angle - (2 * math.pi * angle) / (math.fabs(angle))
    return angle

def bug_service_switch(req):
    request = req.data
    res = SetBoolResponse()
    res.success = True
    res.message = 'Done!'

    if request:
        desired_position_.x = rospy.get_param('des_pos_x')
        desired_position_.y = rospy.get_param('des_pos_y')
        change_state(0)


    return res

def main():
    global regions_, position_, desired_position_, state_, yaw_, yaw_error_allowed_, srv_client_user_interface_, pub
    global srv_client_go_to_point_, srv_client_wall_follower_, srv_client_random_position_

    rospy.init_node('bug0')

    sub_laser = rospy.Subscriber('/scan', LaserScan, clbk_laser)
    sub_odom = rospy.Subscriber('/odom', Odometry, clbk_odom)

    pub = rospy.Publisher('/cmd_vel', Twist, queue_size=1)

    srv = rospy.Service('bug_sevice', SetBool, bug_service_switch)

    srv_client_go_to_point_ = rospy.ServiceProxy('/go_to_point_switch', SetBool)
    srv_client_wall_follower_ = rospy.ServiceProxy('/wall_follower_switch', SetBool)
    srv_client_user_interface_ = rospy.ServiceProxy('/user_input', SetBool)

    rospy.wait_for_service('/go_to_point_switch')
    rospy.wait_for_service('/wall_follower_switch')
    rospy.wait_for_service('/user_input')


    # initialize user input
    change_state(2)
    rate = rospy.Rate(20)

    while not rospy.is_shutdown():
        if regions_ == None:
            continue

        if state_ == 0:
            err_pos = math.sqrt(pow(desired_position_.y - position_.y, 2) + pow(desired_position_.x - position_.x, 2))

            if err_pos < 0.3:
                change_state(2)

            if regions_['front'] < 0.5:
                change_state(1)

        elif state_ == 1:
            desired_yaw = math.atan2(
                desired_position_.y - position_.y, desired_position_.x - position_.x)
            err_yaw = normalize_angle(desired_yaw - yaw_)
            if regions_['front'] > 1 and math.fabs(err_yaw) < 0.05:
                change_state(0)

        rate.sleep()


if __name__ == "__main__":
    main()
