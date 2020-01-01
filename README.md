# Colour-based-detection
OpenCV code to track an object based on its color.
## Requirements
- Rpi 3b+
- Raspi Cam v2 (the best option if you want to use CSI-2 interface)
- OpenCV on raspbian OS
- Other python dependencies are specified in the readme.txt file
## Idea
The goal of the given code is to perform image segmentation using HSV colour space in OpenCV. This is very useful incase you
want to perform color base tracking and not make use of Deep learning or any other Complex Machine Learning algorithm, however 
the accuracy that you get in this solution is not very good and it just gets the job done. 
## Code Flow
Initally we get a frame from raspi cam and we apply filters to smoothen it to reduce noise. We convert the color space from
RGB to HSV because the range of pixels spread in RGB color space is huge as a result of which tracking a particular object
based on its color characteristics is difficult (if we increase the range then it becomes susceptible to noise). In HSV color space the pixel 
distribution in HUE channel is not very large therefore making it quite useful for our use-case. Also to provide adjustment during the code
execution we have provided trackbars (functionality of OpenCV) that allow us to specify upper and lower limits of all 3 channels 
that help to get a mask that filters out our target color using inRange() function. Also we have made use of morphological operations ->
closing and opening ( usage of dilation and erosion) that help us to clear our target image. Our code returns us the bounding box
around the largest contour available in the current frame of the video and also a dot that follows the centre of mass of the bounding
box. 

We also display 2D - frame when the object is detected, along with co-ordinates of COM and also the angle formed by 
it with X and Y axis which can be later used to make gimbals for object tracking. In the terminal using an inaccurate method
of similarity of triangles we are able to calculate the distance to the target object only if know the target object's size (in 
our example we make use of a known lemon).
