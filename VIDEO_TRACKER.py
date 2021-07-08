# import the necessary packages
from tkinter import *
import cv2
import imutils
import time
import csv
from matplotlib import pyplot as plt
from math import log10, floor
from decimal import Decimal
from imutils.video import VideoStream
import argparse

frame_rate = 30

ball_radius = 0.029

colourLower = (1, 0, 0)
colourUpper = (3, 255, 255)

vs = VideoStream(src=1).start()
# allow the camera or video file to warm up
time.sleep(2.0)

# create a csv file to store the coordinates of the center point
with open('center_coordinates.csv', 'w', newline='') as file:
	writer = csv.writer(file)
	writer.writerow(['Frame Index', 'Position of Centroid', 'Position of Centroid', 'Radius'])

	# initialize frame index
	index = 0

	# keep looping
	while True:

		# get frame index
		index += 1
		# grab the current frame
		frame = vs.read()
		# if we are viewing a video and we did not grab a frame, then we have reached the end of the video
		if frame is None:
			break
		# resize the frame, blur it, and convert it to the HSV color space
		# frame = imutils.resize(frame, width=500)
		blurred = cv2.GaussianBlur(frame[139:941, 364:1556], (11, 11), 0) # remove any high-frequency noise
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
				cv2.circle(frame[139:941, 364:1556], (int(x), int(y)), int(radius),
					(0, 255, 255), 2)
				cv2.circle(frame[139:941, 364:1556], center, 5, (0, 0, 255), -1)
			# insert relevant information to the csv
			writer.writerow([index, center[0], center[1], radius])

		# show the frame to our screen
		cv2.imshow("Frame", frame[139:941, 364:1556])
		key = cv2.waitKey(1) & 0xFF
		# if the 'q' key is pressed, stop the loop
		if key == ord("q"):
			break

# close all windows
cv2.destroyAllWindows()

# read the csv file
with open('center_coordinates.csv') as csv_file:
	csv_reader = csv.reader(csv_file, delimiter=',')
	line_count = 0
	time_vec = []
	x_vec = []
	y_vec = []

	# initialize average radius calculations
	radius_to_avg = 0

	for row in csv_reader:
		if line_count == 0:
			pass
		else:
			radius_to_avg += float(row[3])
			time_vec.append(line_count / frame_rate)
			x_vec.append(float(row[1])) # grabs only horizontal motion
			y_vec.append(float(row[2])) # grabs only vertical motion
		line_count += 1

	radius_avg = radius_to_avg / line_count
	meters_per_pixel = ball_radius / radius_avg

	# convert from frames -> seconds and pixels -> meters
	for index in range(0, len(time_vec)):
		x_vec[index] = x_vec[index] * meters_per_pixel
		y_vec[index] = y_vec[index] * meters_per_pixel

	# initialize difference vector for calculation of velocity
	ds_vec_y = []
	ds_vec_x = []
	sub = 0

	# compute differences for difference vector, using central difference method
	for element in time_vec:
		if sub == 0 or sub == len(time_vec) - 1:
			pass
		else:
			# ds_vec.append((x_vec[sub]**2 + y_vec[sub]**2)**0.5 - (x_vec[sub - 1]**2 + y_vec[sub - 1]**2)**0.5)
			ds_vec_y.append((-1*(y_vec[sub + 1] - y_vec[sub - 1])) / 2)
			ds_vec_x.append((x_vec[sub + 1] - x_vec[sub - 1]) / 2)
		sub += 1

	# initialize velocity vector
	vel_vec_y = []
	vel_vec_x = []

	# compute velocity vector, assuming that object is never out of frame (frame rate is constant)
	for i in range(0, len(ds_vec_y)): # same as ds_vec_x
		vel_vec_y.append(ds_vec_y[i] / (1/frame_rate))
		vel_vec_x.append(ds_vec_x[i] / (1/frame_rate))

	fontsize = 10

	# plot velocity against time
	plot0 = plt.subplot(221)
	plt.plot(time_vec[1:-1], vel_vec_x)
	plt.title('Horizontal Velocity Against Time', fontsize=fontsize)
	plt.xlabel('Time [s]', fontsize=fontsize)
	plt.ylabel('Velocity [m/s]', fontsize=fontsize)
	plt.xticks(fontsize=fontsize)
	plt.yticks(fontsize=fontsize)

	# plot velocity against time
	plot1 = plt.subplot(222)
	plt.plot(time_vec[1:-1], vel_vec_y)
	plt.title('Vertical Velocity Against Time', fontsize=fontsize)
	plt.xlabel('Time [s]', fontsize=fontsize)
	plt.ylabel('Velocity [m/s]', fontsize=fontsize)
	plt.xticks(fontsize=fontsize)
	plt.yticks(fontsize=fontsize)

	# plot position against time
	plot2 = plt.subplot(223)
	plt.plot(time_vec, x_vec)
	plt.title('Horizontal Position Against Time', fontsize=fontsize)
	plt.xlabel('Time [s]', fontsize=fontsize)
	plt.ylabel('Horizontal Position [m]', fontsize=fontsize)
	plt.xticks(fontsize=fontsize)
	plt.yticks(fontsize=fontsize)

	# plot position against time, have to reflect about x axis due to opencv coordinate system
	for j in range (0, len(y_vec)):
		y_vec[j] = -1*y_vec[j]

	# plot position against time
	plot2 = plt.subplot(224)
	plt.plot(time_vec, y_vec)
	plt.title('Vertical Position Against Time', fontsize=fontsize)
	plt.xlabel('Time [s]', fontsize=fontsize)
	plt.ylabel('Vertical Position [m]', fontsize=fontsize)
	plt.xticks(fontsize=fontsize)
	plt.yticks(fontsize=fontsize)

	# display plots
	plt.show()

# widget that takes in time interval for analysis
trunk = Tk()
trunk.title("Snip Selection")

# where user inputs interval for analysis
e = Entry(trunk, width=50)
e.pack()

# separate a string into two floats
def getTime(interval):
	global lower, upper
	lower = float(interval[:interval.rfind(",")])
	upper = float(interval[interval.rfind(",") + 1:])
	return(lower, upper)

# run getTime upon button push
myButton = Button(trunk,
			text="Enter two points, separated by a comma, as an interval over which you would like to analyse.",
			command=lambda: getTime(e.get()))
myButton.pack()

trunk.mainloop()

# compute the mean element of an array
def mean(arr):
	mean = 0.0
	# loop across all elements
	for datum in arr:
		mean += datum/len(arr)

	return mean

# compute the variance of an array of data points
def variance(arr):
	avg = mean(arr)
	variance = 0.0
	# variance formula
	for datum in arr:
		variance += (datum - avg)**2/(len(arr)-1) # sum of squares (of differences between our average and our point(s))

	return variance

# compute the standard deviation of an array of data points
def stdev(arr):
	stdev = (variance(arr))**0.5 # variance is s^2, standard deviation is s

	return stdev

# set arbitrarily large values of epsilon, so that a closest number is almost always found
epsilon_l = 100000
epsilon_u = 100000
epsilon_index_l = 0
epsilon_index_u = 0

# find the index of the value that is closest to the input lower and upper time values
epsilon_index_l = min(range(len(time_vec)), key=lambda i: abs(time_vec[i]-lower))
epsilon_index_u = min(range(len(time_vec)), key=lambda i: abs(time_vec[i]-upper))

# crop the velocity vector about the indices found above
cropped_vel = vel_vec_y[epsilon_index_l: epsilon_index_u + 1]

# sanity check for best fit
# print("The mean vertical velocity is", mean(cropped_vel), "with a standard deviation of", stdev(cropped_vel))

# compute the best fit line of the vertical displacement (which is what we care about) over the specified time interval
def lin_uncertainty(arr_y, arr_x): # this works

	N = len(arr_y) # arr_y is of the same length as arr_y

	# initialize the necessary terms
	term_00 = 0 # first thing in the delta eqn (just the sums)
	term_01 = 0 # second thing in the delta eqn (just the sums)
	term_10 = 0 # product of x_i and y_i, gets summed
	term_12 = 0 # sum of y vals

	# compute necessary terms
	for i in range(0, N):
		term_00 += arr_x[i] ** 2
		term_01 += arr_x[i]
		term_10 += arr_x[i] * arr_y[i]
		term_11 = term_01 # they're the same thing, just for consistency
		term_12 += arr_y[i]

	# more miscellaneous math
	delta = N * term_00 - term_01 ** 2

	# slope and intercept estimates
	m = (N * term_10 - term_11 * term_12)/delta
	b = (term_12 - m * term_01)/N

	# compute necessary terms
	s_yx_sum = 0

	# more miscellaneous math
	for j in range(0, N):
		s_yx_sum += (arr_y[j] - b - m * arr_x[j]) ** 2

	# more miscellaneous math
	s_yx_squared = ((1/(N - 2))*(s_yx_sum))

	# uncertainties
	s_m = (N * s_yx_squared / delta) ** 0.5
	s_b = (s_yx_squared * term_00 / delta) ** 0.5

	# sanity check, optional
	# print("The slope is", round(m, abs(int(str((Decimal(s_m)))[str((Decimal(s_m))).rfind("e"):]))) ,
	# 	  "with an uncertainty of", round(s_m, -int(floor(log10(abs(Decimal(s_m)))))))
	# print("The y-intercept is", round(b, abs(int(str((Decimal(s_b)))[str((Decimal(s_b))).rfind("e"):]))),
	# 	  "with an uncertainty of", round(s_b, -int(floor(log10(abs(Decimal(s_b)))))))

	return [round(m, abs(int(str((Decimal(s_m)))[str((Decimal(s_m))).rfind("e"):]))),
			round(s_m, -int(floor(log10(abs(Decimal(s_m))))))]

# uncertainty calculations and propagations
distance = -0.101
distance_uncertainty = 0.001
[m, s_m] = lin_uncertainty(y_vec[epsilon_index_l: epsilon_index_u + 1], time_vec[epsilon_index_l: epsilon_index_u + 1])
time_seconds = distance / m
time_seconds_uncertainty = ((1 / (m) * distance_uncertainty) ** 2 + (distance / (m ** 2) * s_m) ** 2) ** 0.5
time_seconds_uncertainty = round(time_seconds_uncertainty, -int(floor(log10(abs(Decimal(time_seconds_uncertainty))))))
time_minutes_uncertainty = round(time_seconds_uncertainty / 60, -int(floor(log10(abs(Decimal(time_seconds_uncertainty / 60))))))
time_minutes = time_seconds / 60
time_minutes = round(time_minutes, -1*Decimal(str(time_minutes_uncertainty)).as_tuple().exponent)

# final result ! :)
print("The time taken for the ball to fall between the fiduciary lines is", time_minutes, "minutes, with an uncertainty of", time_minutes_uncertainty)
