# CV4Viscosity
**Introduction.<br/>**
The aim of this project is to develop a more accurate method of calculating the viscosity of oil being used in the determination of the skin friction coefficient over complex geometry. This program uses computer vision, instead of human vision, to monitor the descent of a ball through a tube of oil. The time taken for the ball's descent, once it has reached its terminal velocity, is an indicator of the viscosity of the oil. In this program, a video file is specified by the user for analysis. Computer vision is used to identify a ball falling in oil, and track its trajectory on a spreadsheet, which is read to generate plots of the ball's motion. These plots can be examined by a human, who can provide a time interval for analysis, and the program will compute the mean and best-fit velocities, and their associated uncertainties.<br/>
<br/>
**Installation.<br/>**
The code for this can be found on my GitHub, @dnfost. https://github.com/dnfost/CV4Viscosity<br/>
<br/>
**Issues.<br/>**
If one encounters any issues with this code, report it directly on GitHub, or reach out to me. <br/>
<br/>
**Breakdown.<br/>**
This is one of the more long-winded programs that I've written, so I'm writing a basic description of what each section of code does, to better the understanding of the reader. <br/>
<br/>
This program begins with a series of import statements. Make sure that all necessary packages are installed on your system before attempting to run the program. <br/>
<br/>
The first thing that this code actually does is prompts the user to input a video path, then press a button and exit from the widget prompt. This uses the name of the video file from the provided video path and stores it for use in the actual image-tracking part of this program. One thing to note about this video is that it should already be cropped and trimmed appropriately. What I mean by this is that the frames of the video should contain solely the viscometer tube against a white background (I chose white because it is the easiest colour to contrast the stainless steel ball against), and the video should be trimmed to just play the ball's descent. Otherwise, too little cropping or trimming will distract the image-tracker. <br/>
<br/>
Next, parameters such as the camera frame rate measured in fps, the radius of the object measured in m (in this application we are using a ball, which is spherical), as well as the upper and lower bounds of the object's colour in HSV are prompted for the user to input. Default values are provided, but can be edited in the code, since it is assumed that there will not be much variation of camera specs, ball colour, or ball shape over the course of experimentation. Determining the appropriate bounds for the HSV colour space can be quite tedious, as it would necessitate the running of the entire code. Instead, provided as well is "COLOUR\_DEBUGGER.py", which can streamline the process of determining HSV bounds.<br/>
<br/>
The aforementioned video file name is then used as the input for the image-tracking part of the program. <br/>
<br/>
Then, a csv file is made (or opened if it already exists), as a spot for the coordinates of the center of the ball to be written to. Frame by frame, the video is edited to remove noise, and the resultant frame is analyzed for the input colours. If found, a contour is drawn to enclose the colours, and the coordinates of the center of the minimum enclosing circle is written to the csv file. <br/>
<br/>
Upon completion of writing to the csv file, the file is opened again, and the coordinates of the center are used to compute the displacement and velocity of the ball, after conversion from pixels to meters. These values (horizontal and vertical displacement, horizontal and vertical velocity) are plotted onto a single figure. <br/>
<br/>
Informed by the graphs, a user can input a selected time interval, over which the mean and best-fit velocities, along with their associated uncertainties will be computed. From the best-fit velocity, the time required for the ball to fall between the fiduciary lines is computed. <br/>
<br/>
**Contributor Information.**<br/>
Daniel Foster, Summer Research Intern at Flow Control and Experimental Turbulence Lab at the University of Toronto Institute for Aerospace Studies. d.foster@mail.utoronto.ca <br/>
<br/>
**Citation Information.**<br/>
Rosebrock, A (2015) ball_tracking.py source code [Source Code]. https://www.pyimagesearch.com/2015/09/14/ball-tracking-with-opencv/
