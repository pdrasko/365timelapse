365timelapse
============
The following code will process images taken every day by a user, recognize the location of the face using OpenCV and crop for it. The user can then create a video timelapse of the images.

Instructions
============
To generate the files 
	main.py -d '[DIRECTORY_OF_ORIGINAL_IMAGES]' prepare 
	main.py -d '[DIRECTORY_OF_ORIGINAL_IMAGES]' create -f [optional - FRAMERATE]

Requirements
============
ffmpeg
OpenCV 

Based on the following code
===========================
https://github.com/PaulJuliusMartinez/timelapse