import re
import os
import glob
import sys
import FaceImage
from PIL import Image
from PIL.ExifTags import TAGS
from multiprocessing import Pool
from datetime import datetime
from operator import itemgetter

def prepareTimelapse(location, dimensionStr):
	list = {}
	parse = re.match('^(\d+)x(\d+)$', dimensionStr)
	if not parse:
		print 'Your dimension argument of ' + dimensionStr + ' does not meet the "####x####" format.'
		return

	width = '1080'#parse.group(1)
	height = '1920'#parse.group(2)

	imageFiles = glob.glob(location + '/*.[jJ][pP][eE][gG]') + glob.glob(location + '/*.[jJ][pP][gG]')
	
	for imageFile in imageFiles:
		ret = {}
		img = Image.open(imageFile)
		exif_data = img._getexif()
		for tag, value in exif_data.items():
			decoded = TAGS.get(tag, tag)
			ret[decoded] = value
		date = datetime.strptime(ret['DateTimeOriginal'], '%Y:%m:%d %H:%M:%S')
		list[str(date)] = {'file': imageFile, 'date': date}
	imagelist = list.keys()
	imagelist.sort()
	tempFolder = location + '/timelapse_images'
	if os.path.exists(tempFolder):
		os.system('rm -rf ' + location + '/timelapse_images')	

	os.makedirs(tempFolder)

	fileNumber = 0
	pool = Pool()
	print 'Beginning to resize images, prints a "." for each 10 pictures converted. with following dim ' + width + ' x ' + height
	for image in imagelist:
		os.system('convert -pointsize 60 -fill white -draw \'text 1000, 1000 "Day ' + str(list[image]['date'].timetuple().tm_yday)+ '" \' ' + list[image]['file'] + ' -resize ' + width + 'x' + height + '^ ' + location + '/timelapse_images/image' + str(fileNumber).zfill(6) + '.jpg')
		pool.apply_async(FaceImage.runFaceImage, (location + '/timelapse_images/image' + str(fileNumber).zfill(6) + '.jpg', location + '/timelapse_images/image' + str(fileNumber).zfill(6) + '_face.jpg'))
		fileNumber = fileNumber + 1
		if (fileNumber % 10 == 0):
			sys.stdout.write('.')
	pool.close()
	pool.join()



def createTimelapse(location, framerate):
	imageFolder = location + '/timelapse_images'
	if not os.path.exists(imageFolder):
		print 'There is no "timelapse_images" folder in this directory.'
		return

	os.system('ffmpeg -r ' + str(framerate) + ' -i ' + imageFolder + '/image%06d.jpg -sameq ' + location + '/timelapse' + str(framerate) + '.mp4')	




def cleanupTimelapse(location):
	valid = {'yes':True, 'ye':True, 'y':True, 'no':False, 'n':False}

	if os.path.exists(location + '/timelapse_images'):
		sys.stdout.write('Remove timelapse_images directory in ' + location + ' and all its contents?\n')
		while True:
			answer = raw_input().lower()
			if answer in valid:
				if valid[answer]:
					os.system('rm -rf ' + location + '/timelapse_images')
					break;
				else:
					print location + '/timelapse_images was not removed.'
					break;
			else:
				print 'Please respond "yes/no"'
	else:
		print "There's nothing to clean up here."



# Argument handling

import argparse

parser = argparse.ArgumentParser(description='Create a timelapse video')
parser.add_argument('-d', '--directory', type=str, help='relative path to directory with images, must be specified', required=True)
subparsers = parser.add_subparsers(help='prepare or create timelapse')

parser_prepare = subparsers.add_parser('prepare', help='Resizes all images and places in a temporary directory')
parser_prepare.add_argument('-r', '--resize', type=str, default='1920x1080', help='resize images to this size in ####x#### format (e.g., 1920x1080), default no resizing done')
parser_prepare.set_defaults(action = 'prepare')

parser_create = subparsers.add_parser('create', help='Takes all images in temporary directory and creates timelapse video')
parser_create.add_argument('-f', '--framerate', type=int, default=30, help='framerate of produced video')
parser_create.set_defaults(action = 'create')

parser_cleanup = subparsers.add_parser('cleanup', help='Removes timelapse_images folder and images inside it.')
parser_cleanup.set_defaults(action = 'cleanup')

args = parser.parse_args()

location = os.path.abspath(args.directory)
if not os.path.exists(location):
	print 'The path "' + args.directory + '" does not resolve to a valid location.'
	sys.exit()

if args.action == 'prepare':
	prepareTimelapse(location, args.resize)
elif args.action == 'create':
	createTimelapse(location, args.framerate)
elif args.action == 'cleanup':
	cleanupTimelapse(location)
