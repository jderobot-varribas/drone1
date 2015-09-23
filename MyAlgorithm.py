import math
import jderobot
import cv2
import numpy as np
import rectification
from gui.qtimshow import imshow


class MyAlgorithm:
    def __init__(self, sensor):
        self.sensor = sensor
        self.one=True

    def execute(self):
        img = self.sensor.getImage();
        if img is not None:
            #print "Image is: %s, %s"%(str(img.shape),str(img.dtype))
            self.debugImg(img)

            #rectification.run_example(img)

            HSV_GY_low = (28,10,0)
            HSV_GY_upp = (64,255,255)

            hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
            mask = cv2.inRange(hsv, HSV_GY_low, HSV_GY_upp)
            img_out = cv2.bitwise_and(img, img, mask=mask)

            imshow("mask", mask)
            imshow("filtered", img_out)

            # Mark detection
            detect1(img)

    def debugImg(self, img): pass
    """ Decouple Qt SIGNAL by something like abstract function.
    You must override it with a lambda function that calls
    SIGNAL.emit(), or whatever, so it becomes like SLOT syntax
    via SIGNAL.connect(SLOT) but reversed:
    emitterFunct(x) = lambda(x): (SIGNAL.emit(x))
    """


## Green arrow
HSV_G_low = (58, 80, 70)
HSV_G_upp = (64,255,200)

def detect1(img):
    """
    :param img: Detection based on green filter + center of mass
    :return:
    """
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    mask = cv2.inRange(hsv, HSV_G_low, HSV_G_upp)
    imshow("d1:mask", mask.astype(np.uint8))

    contours, hierarchy = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    """ get every contour point (=APPROX_NONE), so we can use perimeter to
    approximate object center of mass"""

    img_poly = img.copy()
    for contour in contours:
        for point in contour:
            x,y = point[0] # each point is a [[x,y]] element. Just remove wrapping array
            cv2.circle(img_poly, (x,y), 1, (255,0,255))

        ''' center from perimeter '''
        m = cv2.moments(contour)
        m00 = m['m00']
        if m00 > 0:
            cx = int(m['m10']/m00)
            cy = int(m['m01']/m00)
            cv2.circle(img_poly, (cx,cy), 2, (255,0,0), -1)

        ''' center from area '''
        (x,y,w,h) = cv2.boundingRect(contour)
        roi = mask[y:y+h,x:x+w]
        m = cv2.moments(roi)
        cx = int(m['m10']/m['m00'])
        cy = int(m['m01']/m['m00'])
        cv2.circle(img_poly, (x+cx,y+cy), 2, (0,0,255), -1)

    imshow("d1:arrow vertex", img_poly)
