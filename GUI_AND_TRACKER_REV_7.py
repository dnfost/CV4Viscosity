# import the necessary packages
from tkinter import *
import cv2
import imutils
import time
import csv
from matplotlib import pyplot as plt
from math import log10, floor
from decimal import Decimal

def click_and_crop(event, x, y, flags, param):
    # grab references to the global variables
    global refPt, cropping

    # if the left mouse button was clicked, record the starting
    # (x, y) coordinates and indicate that cropping is being
    # performed
    if event == cv2.EVENT_LBUTTONDOWN:
        refPt = [(x, y)]
        cropping = True

    # check to see if the left mouse button was released
    elif event == cv2.EVENT_LBUTTONUP:
        # record the ending (x, y) coordinates and indicate that
        # the cropping operation is finished
        refPt.append((x, y))
        cropping = False

        # draw a rectangle around the region of interest
        cv2.rectangle(image, refPt[0], refPt[1], (0, 255, 0), 2)
        cv2.imshow("image", image)

refPts_list = []

# widget that takes in a video path for analysis
root = Tk()
root.title("Video Selection")

# get user input
e = Entry(root, width=50)
e.pack()

# run the playVid function upon button press
myButton = Button(root, text="Enter a video path.", command=lambda: playVid(e.get()))
myButton.pack()

# shorten the filename, play the video
def playVid(filename):
    global filename_shortened
    filename_shortened = filename[filename.rfind("\\") + 1:]

    my_label = Label(root)
    my_label.pack()

root.mainloop()

cap = cv2.VideoCapture(filename_shortened)

while cap.isOpened():
    ret, image = cap.read()
    # image = image[0:838, 364:1556]
    image = image[0:900, 600:1250]
    cv2.imshow("Frame", image)

    key = cv2.waitKey(1)
    if key == ord('q'):
        path = r'C:\Users\Daniel F\PycharmProjects\OpencvPython\frame.jpg'
        image = cv2.imread(path)
        clone = image.copy()
        cv2.namedWindow("image")
        cv2.setMouseCallback("image", click_and_crop)
        # keep looping until the 'q' key is pressed
        while True:
            # display the image and wait for a keypress
            cv2.imshow("image", image)
            key = cv2.waitKey(1) & 0xFF

            # if the 'r' key is pressed, reset the cropping region
            if key == ord("r"):
                image = clone.copy()

            # if the 'c' key is pressed, break from the loop
            elif key == ord("c"):
                break

            elif key == ord("a"):
                refPts_list.append(refPt)
                image = clone.copy()

        # if there are two reference points, then crop the region of interest
        # from the image and display it
        if len(refPt) == 2:
            roi_0 = clone[refPt[0][1]:refPt[1][1], refPt[0][0]:refPt[1][0]]
            cv2.imshow("ROI", roi_0)
            cv2.waitKey(0)

            roi_1 = clone[refPt[0][1]:refPt[1][1], refPt[0][0]:refPt[1][0]]
            cv2.imshow("ROI", roi_1)
            cv2.waitKey(0)

            print(refPts_list)

            break

    if key == ord('p'):
        cv2.imwrite("frame.jpg", image)
        cv2.waitKey(-1)  # wait until any key is pressed
cap.release()
# close all open windows
cv2.destroyAllWindows()

cap = cv2.VideoCapture(filename_shortened)
# getting video from webcam

while cap.isOpened():
    ret, image = cap.read()

    height = image.shape[0]
    width = image.shape[1]

    x1_1, x2_1 = 0, width
    x1_2, x2_2 = 0, width

    y1_1, y2_1 = refPts_list[0][1][1], refPts_list[0][1][1]
    y1_2, y2_2 = refPts_list[1][1][1], refPts_list[1][1][1]

    line_thickness = 2
    cv2.line(image, (x1_1, y1_1), (x2_1, y2_1), (0, 255, 0), thickness=line_thickness)
    cv2.line(image, (x1_2, y1_2), (x2_2, y2_2), (0, 255, 0), thickness=line_thickness)

    cv2.imshow("Image", image)

    key = cv2.waitKey(1) & 0xFF
    # if the 'q' key is pressed, stop the loop
    if key == ord("q"):
        break

cv2.destroyAllWindows()

# widget that takes in a frame rate
stem = Tk()
stem.title("Input Frame Rate")

# provide a default frame rate to streamline the process
e = Entry(stem, width=50)
e.insert(END, '30')  # This is a default value
e.pack()

# run the getFPS function upon button press
myButton = Button(stem, text="Enter a camera frame rate in fps.", command=lambda: getFPS(e.get()))
myButton.pack()


# convert the input string to a float
def getFPS(fps):
    global frame_rate
    frame_rate = float(fps)


stem.mainloop()

# widget that takes in a lower bound and upper bound for the HSV colour space

frame_rate = 30

twig = Tk()
twig.title("Input HSV Colour Lower and Upper Bounds")

# provide a default HSV space to streamline the process
e = Entry(twig, width=50)
e.insert(END, '0,0,0,130,175,110') # This is a default value
e.pack()

# run the getHSV function upon button press
myButton = Button(twig, text="Enter HSV colour bounds, separated by commas.", command=lambda: getHSV(e.get()))
myButton.pack()


# define the lower and upper boundaries of the ball in the HSV color space
# note that these values are in HSV, not BGR, can be found iteratively through experimentation

# split the input string
def getHSV(HSVs):
    global colourLower, colourUpper
    HSVs = HSVs.split(",")
    colourLower = (float(HSVs[0]), float(HSVs[1]), float(HSVs[2]))
    colourUpper = (float(HSVs[3]), float(HSVs[4]), float(HSVs[5]))


twig.mainloop()

vs = cv2.VideoCapture(filename_shortened)
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

        frame = frame[1]
        # if we are viewing a video and we did not grab a frame, then we have reached the end of the video
        if frame is None:
            break

        frame = frame[0:900, 600:1250]
        # resize the frame, blur it, and convert it to the HSV color space
        # frame = imutils.resize(frame, width=500)
        blurred = cv2.GaussianBlur(frame, (11, 11), 0)  # remove any high-frequency noise
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)  # convert video frame from BGR to HSV
        # construct a mask for the color "red", then perform a series of dilations and erosions to remove any small
        # blobs left in the mask
        mask = cv2.inRange(hsv, colourLower, colourUpper)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)
        height = frame.shape[0]

        # find contours in the mask and initialize the current (x, y) center of the ball
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        center = None
        # only proceed if at least one contour was found
        if len(cnts) > 0:  # if a contour was found
            # find the largest contour in the mask, then use it to compute the minimum enclosing circle and centroid
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
            # only proceed if the radius meets a minimum size
            if radius > 10:
                # draw the circle and centroid on the frame, then update the list of tracked points
                cv2.circle(frame, (int(x), int(y)), int(radius),
                           (0, 255, 255), 2)
                cv2.circle(frame, center, 5, (0, 0, 255), -1)

            # insert relevant information to the csv
            writer.writerow([index, center[0], center[1], radius])

        cv2.line(frame, (x1_1, y1_1), (x2_1, y2_1), (0, 255, 0), thickness=line_thickness)
        cv2.line(frame, (x1_2, y1_2), (x2_2, y2_2), (0, 255, 0), thickness=line_thickness)

        # show the frame to our screen
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF
        # if the 'q' key is pressed, stop the loop
        if key == ord("q"):
            break

# close all windows
cv2.destroyAllWindows()

# convert pixels to m
meters_per_pixel = 0.1 / (refPts_list[1][1][1] - refPts_list[0][1][1])
meters_per_pixel_uncertainty = 0.001 / height

# read the csv file
with open('center_coordinates.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    time_vec = []
    x_vec = []
    x_vec_uncertainty = []
    y_vec_uncertainty = []
    y_vec = []

    # convert from frames -> seconds and pixels -> meters
    for row in csv_reader:
        if line_count == 0:
            pass
        else:
            time_vec.append(line_count / frame_rate)
            x_vec.append(meters_per_pixel * float(row[1]))  # grabs only horizontal motion
            x_vec_uncertainty.append(meters_per_pixel_uncertainty * float(row[1]))
            y_vec_uncertainty.append(meters_per_pixel_uncertainty * float(row[2]))
            y_vec.append(meters_per_pixel * float(row[2]))  # grabs only vertical motion
        line_count += 1

    x_vec_plus = []
    x_vec_minus = []
    y_vec_plus = []
    y_vec_minus = []

    for element in range(0, len(x_vec)):
        x_vec_plus.append(x_vec[element] + x_vec_uncertainty[element])
        x_vec_minus.append(x_vec[element] - x_vec_uncertainty[element])
        y_vec_plus.append(y_vec[element] + y_vec_uncertainty[element])
        y_vec_minus.append(y_vec[element] - y_vec_uncertainty[element])

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
            ds_vec_y.append((-1 * (y_vec[sub + 1] - y_vec[sub - 1])) / 2)
            ds_vec_x.append((x_vec[sub + 1] - x_vec[sub - 1]) / 2)
        sub += 1

    # initialize velocity vector
    vel_vec_y = []
    vel_vec_x = []

    # compute velocity vector, assuming that object is never out of frame (frame rate is constant)
    for i in range(0, len(ds_vec_y)):  # same as ds_vec_x
        vel_vec_y.append(ds_vec_y[i] / (1 / frame_rate))
        vel_vec_x.append(ds_vec_x[i] / (1 / frame_rate))

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
    plt.plot(time_vec, x_vec, time_vec, x_vec_plus, time_vec, x_vec_minus)
    plt.title('Horizontal Position Against Time', fontsize=fontsize)
    plt.xlabel('Time [s]', fontsize=fontsize)
    plt.ylabel('Horizontal Position [m]', fontsize=fontsize)
    plt.xticks(fontsize=fontsize)
    plt.yticks(fontsize=fontsize)

    # plot position against time, have to reflect about x axis due to opencv coordinate system
    for j in range(0, len(y_vec)):
        y_vec[j] = -1 * y_vec[j]
        y_vec_plus[j] = -1 * y_vec_plus[j]
        y_vec_minus[j] = -1 * y_vec_minus[j]

    # plot position against time
    plot2 = plt.subplot(224)
    plt.plot(time_vec, y_vec, time_vec, y_vec_plus, time_vec, y_vec_minus)
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
    return (lower, upper)


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
        mean += datum / len(arr)

    return mean


# compute the variance of an array of data points
def variance(arr):
    avg = mean(arr)
    variance = 0.0
    # variance formula
    for datum in arr:
        variance += (datum - avg) ** 2 / (
                    len(arr) - 1)  # sum of squares (of differences between our average and our point(s))

    return variance


# compute the standard deviation of an array of data points
def stdev(arr):
    stdev = (variance(arr)) ** 0.5  # variance is s^2, standard deviation is s

    return stdev


# set arbitrarily large values of epsilon, so that a closest number is almost always found
epsilon_l = 100000
epsilon_u = 100000
epsilon_index_l = 0
epsilon_index_u = 0

# find the index of the value that is closest to the input lower and upper time values
epsilon_index_l = min(range(len(time_vec)), key=lambda i: abs(time_vec[i] - lower))
epsilon_index_u = min(range(len(time_vec)), key=lambda i: abs(time_vec[i] - upper))

# crop the velocity vector about the indices found above
cropped_vel = vel_vec_y[epsilon_index_l: epsilon_index_u + 1]


# sanity check for best fit
# print("The mean vertical velocity is", mean(cropped_vel), "with a standard deviation of", stdev(cropped_vel))

# compute the best fit line of the vertical displacement (which is what we care about) over the specified time interval
def lin_uncertainty(arr_y, arr_x):  # this works

    N = len(arr_y)  # arr_y is of the same length as arr_y

    # initialize the necessary terms
    term_00 = 0  # first thing in the delta eqn (just the sums)
    term_01 = 0  # second thing in the delta eqn (just the sums)
    term_10 = 0  # product of x_i and y_i, gets summed
    term_12 = 0  # sum of y vals

    # compute necessary terms
    for i in range(0, N):
        term_00 += arr_x[i] ** 2
        term_01 += arr_x[i]
        term_10 += arr_x[i] * arr_y[i]
        term_11 = term_01  # they're the same thing, just for consistency
        term_12 += arr_y[i]

    # more miscellaneous math
    delta = N * term_00 - term_01 ** 2

    # slope and intercept estimates
    m = (N * term_10 - term_11 * term_12) / delta
    b = (term_12 - m * term_01) / N

    # compute necessary terms
    s_yx_sum = 0

    # more miscellaneous math
    for j in range(0, N):
        s_yx_sum += (arr_y[j] - b - m * arr_x[j]) ** 2

    # more miscellaneous math
    s_yx_squared = ((1 / (N - 2)) * (s_yx_sum))

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
distance = -0.10
distance_uncertainty = 0.001
[m, s_m] = lin_uncertainty(y_vec[epsilon_index_l: epsilon_index_u + 1], time_vec[epsilon_index_l: epsilon_index_u + 1])
[m_minus, s_m_minus] = lin_uncertainty(y_vec_minus[epsilon_index_l: epsilon_index_u + 1],
                                       time_vec[epsilon_index_l: epsilon_index_u + 1])
[m_plus, s_m_plus] = lin_uncertainty(y_vec_plus[epsilon_index_l: epsilon_index_u + 1],
                                     time_vec[epsilon_index_l: epsilon_index_u + 1])
time_seconds = distance / m
time_seconds_plus = distance / m_plus
time_seconds_minus = distance / m_minus
time_seconds_uncertainty = ((1 / (m) * distance_uncertainty) ** 2 + (distance / (m ** 2) * s_m) ** 2) ** 0.5
time_seconds_uncertainty = round(time_seconds_uncertainty, -int(floor(log10(abs(Decimal(time_seconds_uncertainty))))))
time_minutes_uncertainty = round(time_seconds_uncertainty / 60,
                                 -int(floor(log10(abs(Decimal(time_seconds_uncertainty / 60))))))
time_seconds_uncertainty_plus = ((1 / (m_plus) * distance_uncertainty) ** 2 + (
            distance / (m_plus ** 2) * s_m_plus) ** 2) ** 0.5
time_seconds_uncertainty_plus = round(time_seconds_uncertainty_plus,
                                      -int(floor(log10(abs(Decimal(time_seconds_uncertainty_plus))))))
time_minutes_uncertainty_plus = round(time_seconds_uncertainty_plus / 60,
                                      -int(floor(log10(abs(Decimal(time_seconds_uncertainty_plus / 60))))))
time_seconds_uncertainty_minus = ((1 / (m_minus) * distance_uncertainty) ** 2 + (
            distance / (m_minus ** 2) * s_m_minus) ** 2) ** 0.5
time_seconds_uncertainty_minus = round(time_seconds_uncertainty_minus,
                                       -int(floor(log10(abs(Decimal(time_seconds_uncertainty_minus))))))
time_minutes_uncertainty_minus = round(time_seconds_uncertainty_minus / 60,
                                       -int(floor(log10(abs(Decimal(time_seconds_uncertainty_minus / 60))))))
time_minutes = time_seconds / 60
time_minutes_plus = time_seconds_plus / 60
time_minutes_minus = time_seconds_minus / 60
time_minutes = round(time_minutes, -1 * Decimal(str(time_minutes_uncertainty)).as_tuple().exponent)
time_minutes_plus = round(time_minutes_plus, -1 * Decimal(str(time_minutes_uncertainty_plus)).as_tuple().exponent)
time_minutes_minus = round(time_minutes_minus, -1 * Decimal(str(time_minutes_uncertainty_minus)).as_tuple().exponent)

# final result ! :)
print("The time taken for the ball to fall between the fiduciary lines is", time_minutes,
      ". Accounting for uncertainty, the time will be between", time_minutes_plus, "and", time_minutes_minus)
