# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import numpy as np
import math

#***********************************************************************
def nothing(X):
    pass
def find_biggest_contour(image):

    # Copy to prevent modification
    image = image.copy()
    _,contours, hierarchy = cv2.findContours(image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    
    # If no contours are found then we return simply return nothing
    if(len(contours)==0):
        return -1,-1,-1

    # Isolate largest contour
    contour_sizes = [(cv2.contourArea(contour), contour) for contour in contours]
    biggest_contour = max(contour_sizes, key=lambda x: x[0])[1]

    # Empty image mask with black background
    mask = np.zeros(image.shape, np.uint8)
    # Applying the largest contour on the empty image of zeros
    cv2.drawContours(mask, [biggest_contour], -1, 255, -1)
    return 1,biggest_contour, mask

def main_processing(image,lh,ls,lv,uh,us,uv):
    # Convert from BGR to RGB since in opencv we make use of bgr format
    #image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


    # Resize to a third of the size
    # We are trying to process a frame on RPI cpu therefore scaling an image down helps reduce details and thereby less processing strain
    image = cv2.resize(image, None, fx=1/3, fy=1/3)


    # Removing the unecessary noise in the image and making the edges prominent
    # Low pass filter useful for removing noise (high frequency content)
    # High Pass filter good for edge detection

    # 7x7 kernel size  always odd the kernel's number positioning is like a gaussian curve (image smooth)
    image_blur = cv2.GaussianBlur(image, (7, 7), 0)

    # After applying the gauss blur change the colour scheme
    # HSV Scale is ideal to use in this case because here we talk about colour segementation and in this format we can easily extract the colour based on hue
    # Converting BGR to HSV allows to extract a colored object
    image_blur_hsv = cv2.cvtColor(image_blur, cv2.COLOR_BGR2HSV)

    # 30- 50 hue based extraction of lemon yellow
    yellow_min_hue1 = np.array([lh, ls, lv])
    yellow_max_hue1 = np.array([uh, us, uv])
    yellow_mask1 = cv2.inRange(image_blur_hsv, yellow_min_hue1, yellow_max_hue1)

    #The inRange operations allow us to extract the yellow portion of the image thereby we get our target object lemon
    yellow = yellow_mask1 

    # We can build a box kernel from np.ones but since our object is elliptical in shape we make use of this function
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))

    # Fill small gaps
    yellow_closed = cv2.morphologyEx(yellow, cv2.MORPH_CLOSE, kernel)

    # Remove specks
    yellow_net = cv2.morphologyEx(yellow_closed, cv2.MORPH_OPEN, kernel)

    #After cleaning the image we get the biggest contour
    check,big_contour, yellow_mask = find_biggest_contour(yellow_net)
    if(check==-1):
        return

    # Centre of mass
    moments = cv2.moments(yellow_mask)
    centre_of_mass = int(moments['m10'] / moments['m00']), int(moments['m01'] / moments['m00'])

    cv2.circle(image, centre_of_mass, 1, (0, 255, 0), -1)

    # Bounding Rectangle on the actual image after getting the largest contour
    x,y,w,h = cv2.boundingRect(big_contour)
    cv2.rectangle(image, (x,y),(x+w,y+h), (0,255,0), 2)
 
    # Based on the focal length and avg size of target lemon we use similarity of triangles to get the distance from the target
    est_dist=(50*14)//w
    print(est_dist)
    
    # Creation of axes on the image frame only when the object is detcted
    x_half=image.shape[0]//2
    y_half=image.shape[1]//2
    cv2.line(image,(x_half,0),(x_half,image.shape[0]),(0,255,0),1)
    cv2.line(image,(0,y_half),(image.shape[1],y_half),(0,255,0),1)
    
    # Calculation of the angle formed by the COM of the object with X axis and Y axis
    anglex=int(math.degrees(math.atan((centre_of_mass[0]-x_half)/50)))
    angley=int(math.degrees(math.atan((-centre_of_mass[1]+y_half)/50)))
    
    # Displaying the computed values
    text="X {} , Y {}, Xd : {} ,Yd:{}".format(str(centre_of_mass[0]-x_half),str(-centre_of_mass[1]+y_half),str(anglex),str(angley))
    cv2.putText(image,text,(image.shape[0]-140,image.shape[1]-20),cv2.FONT_HERSHEY_PLAIN,0.5,(0,255,0),1)
    image=cv2.resize(image,(600,600),interpolation=cv2.INTER_LINEAR)
    return image


#***********************************************************************
# Main code backbone
#***********************************************************************


# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (600, 600)
camera.framerate = 20
rawCapture = PiRGBArray(camera, size=(600, 600))

# allow the camera to warmup
time.sleep(0.1)
lowhue=0
lowsat=0
lowval=0
upphue=0
uppsat=0
uppval=0
ctr=0
# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    # grab the raw NumPy array representing the image, then initialize the timestamp
    # and occupied/unoccupied text
    image = frame.array
    # show the frame
    val=main_processing(image,lowhue,lowsat,lowval,upphue,uppsat,uppval)
    if val is None:
        cv2.imshow("Frame",image)
    else:
        cv2.imshow("Frame",val)
    key = cv2.waitKey(1)

    if (ctr==0):
        # create trackbars for color change
        cv2.namedWindow('Frame')
        cv2.createTrackbar('LH','Frame',0,255,nothing)
        cv2.createTrackbar('LS','Frame',0,255,nothing)
        cv2.createTrackbar('LV','Frame',0,255,nothing)
        
        cv2.createTrackbar('UH','Frame',0,255,nothing)
        cv2.createTrackbar('US','Frame',0,255,nothing)
        cv2.createTrackbar('UV','Frame',0,255,nothing)
        ctr+=1  
    lowhue = cv2.getTrackbarPos('LH','Frame')
    lowsat = cv2.getTrackbarPos('LS','Frame')
    lowval = cv2.getTrackbarPos('LV','Frame')
    upphue = cv2.getTrackbarPos('UH','Frame')
    uppsat = cv2.getTrackbarPos('US','Frame')
    uppval = cv2.getTrackbarPos('UV','Frame')
    # clear the stream in preparation for the next frame
    rawCapture.truncate(0)

    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break
    
    #time.sleep(0.1)
camera.close()
cv2.destroyAllWindows()