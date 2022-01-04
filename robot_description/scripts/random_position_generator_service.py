#! /usr/bin/env python

import rospy
from random import random
from std_srvs.srv import *

import math


minx_ = -8.0
maxx_ = 8.0
miny_ = -8.0
maxy_ = 8.0

def generate(msg):
    global minx_, maxx_, miny_, maxy_
    valuex = random()
    valuey = random()
    valuex = minx_ + (valuex * (maxx_ - minx_))
    valuey = miny_ + (valuey * (maxy_ - miny_))
    rospy.set_param('des_pos_x', valuex)
    rospy.set_param('des_pos_y', valuey)
    
    print('\n\nRANDOMPOSGEN:: Desired Position is set to [' + str(valuex) + ', ' + str(valuey) + ']\n\n')

    res = SetBoolResponse()
    res.success = True
    res.message = 'Done!'
    return res

def take_action():
    global regions_
    regions = regions_
    msg = Twist()
    linear_x = 0
    angular_z = 0
    state_description = ''

    d0 = 1
    d = 1.5

    if regions['front'] > d0 and regions['fleft'] > d and regions['fright'] > d:
        state_description = 'case 1 - nothing'
        change_state(0)
    elif regions['front'] < d0 and regions['fleft'] > d and regions['fright'] > d:
        state_description = 'case 2 - front'
        change_state(1)
    elif regions['front'] > d0 and regions['fleft'] > d and regions['fright'] < d:
        state_description = 'case 3 - fright'
        change_state(2)
    elif regions['front'] > d0 and regions['fleft'] < d and regions['fright'] > d:
        state_description = 'case 4 - fleft'
        change_state(0)
    elif regions['front'] < d0 and regions['fleft'] > d and regions['fright'] < d:
        state_description = 'case 5 - front and fright'
        change_state(1)
    elif regions['front'] < d0 and regions['fleft'] < d and regions['fright'] > d:
        state_description = 'case 6 - front and fleft'
        change_state(1)
    elif regions['front'] < d0 and regions['fleft'] < d and regions['fright'] < d:
        state_description = 'case 7 - front and fleft and fright'
        change_state(1)
    elif regions['front'] > d0 and regions['fleft'] < d and regions['fright'] < d:
        state_description = 'case 8 - fleft and fright'
        change_state(0)
    else:
        state_description = 'unknown case'
        rospy.loginfo('RANDOMPOSGEN:: ' + regions)


def main():

    rospy.init_node('random_position_generator_service')

    srv = rospy.Service('generate_random_position', SetBool, generate)

    rate = rospy.Rate(20)
    while not rospy.is_shutdown():
        rate.sleep()


if __name__ == '__main__':
    main()
