#!/usr/bin/env python3

import cozmo
import argparse
#import rospy
#import cv2
def cozmo_program(robot: cozmo.robot.Robot):
    parser = argparse.ArgumentParser()
    parser.add_argument('word', type=str, help="words you want cozmo to say.")
    args = parser.parse_args()
    robot.say_text("{}".format(args.word),play_excited_animation=True, use_cozmo_voice=True,duration_scalar=1.9, voice_pitch=1.0).wait_for_completed()

cozmo.robot.Robot.drive_off_charger_on_connect = False
cozmo.run_program(cozmo_program)
