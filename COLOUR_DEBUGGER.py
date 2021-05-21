from tkinter import *
from tkvideo import tkvideo

import cv2
import imutils
import time

root = Tk()
root.title("Video Selection and Preview")

e = Entry(root, width=50)
e.pack()

myButton = Button(root, text="Enter a video path.", command=lambda: playVid(e.get()))
myButton.pack()

def playVid(filename):

	global filename_shortened
	filename_shortened = filename[filename.rfind("\\") + 1:]

	my_label = Label(root)
	my_label.pack()

root.mainloop()

twig = Tk()
twig.title("Input HSV Colour Lower and Upper Bounds")

e = Entry(twig, width=50)
e.insert(END, '40,20,0,400,480,100') # This is a default value
e.pack()

myButton = Button(twig, text="Enter HSV colour bounds, separated by commas.", command=lambda: getHSV(e.get()))
myButton.pack()

# define the lower and upper boundaries of the ball in the HSV color space
# note that these values are in HSV, not BGR, can be found iteratively through experimentation

def getHSV(HSVs):

    global colourLower, colourUpper
    HSVs = HSVs.split(",")
    colourLower = (float(HSVs[0]), float(HSVs[1]), float(HSVs[2]))
    colourUpper = (float(HSVs[3]), float(HSVs[4]), float(HSVs[5]))

twig.mainloop()

vs = cv2.VideoCapture(filename_shortened)
# allow the camera or video file to warm up
time.sleep(2.0)

# keep looping
while True:
	# grab the current frame
	frame = vs.read()

	# handle the frame from VideoCapture or VideoStream
	frame = frame[1]
	# if we are viewing a video and we did not grab a frame, then we have reached the end of the video
	if frame is None:
		break
	# resize the frame, blur it, and convert it to the HSV color space
	frame = imutils.resize(frame, width=500)
	blurred = cv2.GaussianBlur(frame, (11, 11), 0) # remove any high-frequency noise
	hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV) # convert video frame from BGR to HSV
	# construct a mask for the color "red", then perform a series of dilations and erosions to remove any small
	# blobs left in the mask
	mask = cv2.inRange(hsv, colourLower, colourUpper)
	mask = cv2.erode(mask, None, iterations=2)
	mask = cv2.dilate(mask, None, iterations=2)

	# find contours in the mask and initialize the current (x, y) center of the ball
	cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	cnts = imutils.grab_contours(cnts)
	center = None
	# only proceed if at least one contour was found
	if len(cnts) > 0: # if a contour was found
		# find the largest contour in the mask, then use it to compute the minimum enclosing circle and centroid
		c = max(cnts, key=cv2.contourArea)
		((x, y), radius) = cv2.minEnclosingCircle(c)
		M = cv2.moments(c)
		center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
		# only proceed if the radius meets a minimum size
		if radius > 10:
			# draw the circle and centroid on the frame, then update the list of tracked points
			cv2.circle(frame, (int(x), int(y)), int(radius),(0, 255, 255), 2)
			cv2.circle(frame, center, 5, (0, 0, 255), -1)

		# show the frame to our screen
		cv2.imshow("Frame", frame)
		key = cv2.waitKey(1) & 0xFF
		# if the 'q' key is pressed, stop the loop
		if key == ord("q"):
			break

vs.release()
# close all windows
cv2.destroyAllWindows()