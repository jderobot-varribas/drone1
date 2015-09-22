import math
import jderobot
import cv2
import numpy as np
import rectification
import gui.minimal_gui as qtui


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

            qtui.qimshow(mask, "mask", qtui.QImage.Format_Indexed8)
            qtui.qimshow(img_out, "filtered")

    def debugImg(self, img): pass
    """ Decouple Qt SIGNAL by something like abstract function.
    You must override it with a lambda function that calls
    SIGNAL.emit(), or whatever, so it becomes like SLOT syntax
    via SIGNAL.connect(SLOT) but reversed:
    emitterFunct(x) = lambda(x): (SIGNAL.emit(x))
    """