
# import the necessary packages
from collections import deque
import numpy as np
import argparse
import imutils
import math
import cv2
 
# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
	help="path to the (optional) video file")
ap.add_argument("-b", "--buffer", type=int, default=64,
	help="max buffer size")
args = vars(ap.parse_args())

greenLower = (100, 86, 6)
greenUpper = (180, 255, 255)
pts = deque(maxlen=args["buffer"])
 

if not args.get("video", False):
	camera = cv2.VideoCapture(1)
 
else:
	camera = cv2.VideoCapture(args["video"])

i = 0

while True:
	i += 0	
	(grabbed, frame) = camera.read()
 
	
	if args.get("video") and not grabbed:
		break
 
	frame = imutils.resize(frame, width=600)
	left = frame[0:300, 0:600]
	right = frame[300:600, 0:600]

	blurred = cv2.GaussianBlur(frame, (11, 11), 0)
	hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
 
	mask = cv2.inRange(hsv, greenLower, greenUpper)
	mask = cv2.erode(mask, None, iterations=2)
	mask = cv2.dilate(mask, None, iterations=2)
	# find contours in the mask and initialize the current
	# (x, y) center of the ball

	# only proceed if at least one contour was found
	cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)[-2]
	center = None
 
	# only proceed if at least one contour was found
	if len(cnts) > 0:
		# find the largest contour in the mask, then use
		# it to compute the minimum enclosing circle and
		# centroid
		c = max(cnts, key=cv2.contourArea)
		((x, y), radius) = cv2.minEnclosingCircle(c)
		M = cv2.moments(c)
		center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
 
		# only proceed if the radius meets a minimum size
		if radius > 10:
			# draw the circle and centroid on the frame,
			# then update the list of tracked points
			cv2.circle(frame, (int(x), int(y)), int(radius),
				(0, 255, 255), 2)
			cv2.circle(frame, center, 5, (0, 0, 255), -1)

		area = math.pi*(radius**2)
		print(area)
 
	# update the points queue
	pts.appendleft(center)

	for i in range(1, len(pts)):
		# if either of the tracked points are None, ignore
		# them
		if pts[i - 1] is None or pts[i] is None:
			continue
 
		
		thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
		cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)

		f = pts[i][0]
		i = pts[i-1][0]
		speed = (f-i)
		#print(speed)


	

	'''if (center[0] > 400):
		print("Right")

	elif (center[1] < 200):
		print("Left")		
 	
	else:
 		print("Center")'''
	

	# show the frame to our screen
	cv2.imshow("Frame", frame)
	cv2.imshow("mask", mask)
	key = cv2.waitKey(1) & 0xFF
 
	# if the 'q' key is pressed, stop the loop
	if key == ord("q"):
		break
 
# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()	
