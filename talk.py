#!/usr/bin/env python3

import cozmo
import argparse

def cozmo_program(robot: cozmo.robot.Robot):
    parser = argparse.ArgumentParser()
    parser.add_argument('word', type=str, help="words you want cozmo to say.")
    args = parser.parse_args()
    robot.say_text("{}".format(args.word)).wait_for_completed()

cozmo.robot.Robot.drive_off_charger_on_connect = False
cozmo.run_program(cozmo_program)
