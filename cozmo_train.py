#!/usr/bin/env python3

# Copyright (c) 2016 Anki, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License in the file LICENSE.txt or at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import time
import os
from datetime import datetime
import cozmo
import tty, sys, termios, select
from cozmo.util import degrees, distance_mm, speed_mmps
import pandas as pd
import shutil

try:
    from PIL import ImageDraw, ImageFont, Image
    import numpy as np
except ImportError:
    sys.exit('run `pip3 install --user Pillow numpy` to run this example')

def demo_camera_exposure(robot: cozmo.robot.Robot):
	camera = robot.camera
	camera.color_image_enabled = False
	camera.enable_auto_exposure()

def set_init_pose(robot: cozmo.robot.Robot):
	robot.set_lift_height(1.0, in_parallel=True)
	robot.set_head_angle(degrees(0.0), in_parallel=True)

key_list = []
img_list = []

def getKey(robot: cozmo.robot.Robot):
	global key_list
	global img_list
	fd = sys.stdin.fileno()
	settings = termios.tcgetattr(fd)
	#try:
	tty.setraw(sys.stdin.fileno())
	rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
	if rlist:
		key = sys.stdin.read(1)
		key_list.append(key)
		latest_image = robot.world.latest_image
		latest_img = np.array(latest_image.raw_image)
		im = Image.fromarray(latest_img)
		timestamp = datetime.now().strftime('%Y_%m_%d_%H_%M_%S_%f')[:-3]
		img_list.append('{}/{}.jpg'.format(args.image_folder,timestamp))
		image_filename = os.path.join(args.image_folder, timestamp)
		im.save('{}.jpg'.format(image_filename))
	else:
		key = ''
	#finally:
	termios.tcsetattr(fd, termios.TCSADRAIN, settings)
	return key

moveBindings = {
				'i':(100, 100),
				',':(-100, -100),
				'j':(50, 150),
				'l':(150, 50),
				'k':(0, 0),
				' ':(0, 0)
				}

def cozmo_program(robot: cozmo.robot.Robot):
	lw = 0
	rw = 0
	count = 0
	set_init_pose(robot)
	demo_camera_exposure(robot)
	while True:
		start = time.time()
		key = getKey(robot)
		cozmo.logger.info("'{}' key pressed".format(key))
		if key in moveBindings.keys():
			lw = moveBindings[key][0]
			rw = moveBindings[key][1]
			count = 0
		else:
			count = count + 1
			if count > 4:
				lw = 0
				rw = 0
			if key == 'q' or key == '\x03':
				data = [('img', img_list),
						('key', key_list)
						]
				df = pd.DataFrame.from_items(data)
				df.to_csv('driving_log.csv')
				cozmo.logger.info('Writing to csv file, Exiting')
				break
		robot.drive_wheels(lw, rw)
		ls = robot.left_wheel_speed
		rs = robot.right_wheel_speed
		cozmo.logger.info('cmd left, right speed: {}, {}'.format(lw, rw))
		cozmo.logger.info('fb left,right  speed: {}, {}'.format(ls, rs))

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Remote Driving')
	parser.add_argument(
        'image_folder',
        type=str,
        nargs='?',
        default='',
        help='Path to image folder. This is where the images from the run will be saved.'
	)	
	args = parser.parse_args()
	if args.image_folder != '':
		cozmo.logger.info("Creating image folder at {}".format(args.image_folder))
		if not os.path.exists(args.image_folder):
			os.makedirs(args.image_folder)
		else:
			shutil.rmtree(args.image_folder)
			os.makedirs(args.image_folder)
		cozmo.logger.info("RECORDING THIS RUN ...")
	else:
		cozmo.logger.info("NOT RECORDING THIS RUN ...")
	cozmo.setup_basic_logging()
	cozmo.robot.Robot.drive_off_charger_on_connect = False
	cozmo.run_program(cozmo_program, use_viewer=True, force_viewer_on_top=True)

