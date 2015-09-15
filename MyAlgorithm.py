import math
import jderobot
import cv2
import numpy as np
import rectification


class MyAlgorithm:
    def __init__(self, sensor):
        self.sensor = sensor
        self.one=True

    def execute(self):
        img = self.sensor.getImage();
        if img is not None:
            #print "Image is: %s, %s"%(str(img.shape),str(img.dtype))
            self.debugImg(img)

            rectification.run_example(img)

    def debugImg(self, img): pass
    """ Decouple Qt SIGNAL by something like abstract function.
    You must override it with a lambda function that calls
    SIGNAL.emit(), or whatever, so it becomes like SLOT syntax
    via SIGNAL.connect(SLOT) but reversed:
    emitterFunct(x) = lambda(x): (SIGNAL.emit(x))
    """