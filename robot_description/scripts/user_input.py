#! /usr/bin/env python

import rospy
from std_srvs.srv import *
from geometry_msgs.msg import Twist
from pynput import keyboard

pub = None
listener = None
active_ = False
srv_client_random_position_ = None
srv_bug_ = None

def go_straight():
    global pub
    twist_msg = Twist()
    twist_msg.linear.x = 0.5
    twist_msg.angular.z = 0
    pub.publish(twist_msg)
    return True
def go_backward():
    global pub
    twist_msg = Twist()
    twist_msg.linear.x = -0.5
    twist_msg.angular.z = 0
    pub.publish(twist_msg)
    return True
def turn_left():
    global pub
    twist_msg = Twist()
    twist_msg.linear.x = 0
    twist_msg.angular.z = -0.5
    pub.publish(twist_msg)
    return True
def turn_right():
    global pub
    twist_msg = Twist()
    twist_msg.linear.x = 0
    twist_msg.angular.z = 0.5
    pub.publish(twist_msg)
    return True
def stop_robot():
    global pub
    twist_msg = Twist()
    twist_msg.linear.x = 0
    twist_msg.angular.z = 0
    pub.publish(twist_msg)
    return True    

def on_press(key):
    global active_, srv_client_random_position_, srv_bug_
    try:
        if key.char == 'r' or key.char == 'R':
            stop_robot()
            # call for random position generation
            resp = srv_client_random_position_(True)
            # deactivate user control
            active_ = False
            print('USER INPUT:: Random Position Generation Called.')
            activate_listener(False)
            # activate bug.py
            if resp.success:
                srv_bug_(True)
    except AttributeError:
        if str(key) == 'Key.up':
            go_straight()
        elif str(key) == 'Key.down':
            go_backward()
        elif str(key) == 'Key.left':
            turn_left()
        elif str(key) == 'Key.right':
            turn_right()

def on_release(key):
    if key == keyboard.Key.esc:
        # Stop listener
        active_ = False
        activate_listener(False)
        return False 
    else:
        stop_robot()

def user_input_switch(req):
    global active_

    active_ = req.data
    res = SetBoolResponse()
    res.success = True
    res.message = 'Done!'
    if active_ :
        activate_listener(True)
    return res


def activate_listener(stat):
    global listener
    if stat:
        print('USER INPUT:: USER INPUT Service Activated!')
        print('USER INPUT:: ###################################################')
        print('USER INPUT:: Control the robot using Arrow keys on the keyboard.')
        print('USER INPUT:: Press R key for random position and ESC to escape.')
        print('USER INPUT:: ###################################################')

        listener = None
        listener = keyboard.Listener( on_press=on_press,on_release=on_release)
        listener.start()
    else:
        print('USER INPUT:: USER INPUT Service Deactivated!')


def main():
    global pub, active_, listener, srv_client_random_position_, srv_bug_
    rospy.init_node('user_input')

    srv = rospy.Service('user_input', SetBool, user_input_switch)

    srv_bug_ = rospy.ServiceProxy('/bug_sevice', SetBool)
    srv_client_random_position_ = rospy.ServiceProxy('/generate_random_position', SetBool)
    rospy.wait_for_service('/generate_random_position')
    rospy.wait_for_service('/bug_sevice')

    listener = keyboard.Listener( on_press=on_press,on_release=on_release)

    pub = rospy.Publisher('/cmd_vel', Twist, queue_size=1)

    rate = rospy.Rate(20)
    while not rospy.is_shutdown():
        if active_:
            continue
        else:
            listener.stop()
            rate.sleep()


if __name__ == '__main__':
    main()
