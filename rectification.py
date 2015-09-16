#
#  Copyright (C) 1997-2015 JDE Developers Team
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see http://www.gnu.org/licenses/.
#  Authors :
#       Victor Arribas <v.arribas.urjc@gmail.com>

import cv2
import numpy as np
import threading


def run_example(img):
    imgd = img.copy()

    ## OpenCV and PyQt not seems to be compatible. So execute is with --no-gui option
    # Also, after Qt problem solved, create his own thread is only a option.
    clickgui = ClickGUIcv(imgd)
    if 0:
        clickgui.start()
        clickgui.join()
    else:
        clickgui.run()
    points=clickgui.click_data

    ## Retrieved points are (4x2), but boundingBox requires a (4x1x2) mat, so...
    points = points.reshape((4,1,2))

    ## Create fixed rectangle
    rect = cv2.boundingRect(points)
    (x,y,w,h) = rect
    p0 = (x,y); p1=(x+w,y); p2=(x,y+h); p3 = (x+w,y+h)
    cv2.rectangle(imgd, p0,p3, (255,255,255))
    cv2.imshow('bouding rect', imgd)
    cv2.waitKey(100)

    ## Clockwise point mapping (also a 4x1 Mat of 2-channels)
    ref_points = np.array([p0,p1,p3,p2]).reshape((4,1,2))

    ## Obtain perspective transform via OpenCV:
    tf = cv2.getPerspectiveTransform(points.astype(np.float32), ref_points.astype(np.float32))
    tf = calculePerspectiveTransform(points.reshape((4,2)), ref_points.reshape((4,2)))
    print 'points=',points
    print 'ref_points=',ref_points
    print 'tf=',tf

    ## Apply transform
    img0 = cv2.warpPerspective(img, tf, (img.shape[1], img.shape[0]))
    cv2.imshow('rectified', img0)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    cv2.waitKey(1)


class ClickGUIcv(threading.Thread):
    def __init__(self, img, name='Click GUI'):
        threading.Thread.__init__(self)
        self.setDaemon(True)

        self.win_name = name
        self.img = img

        self.count=0
        self.click_data=np.zeros((4,2), np.int32)

    def run(self):
        cv2.namedWindow(self.win_name)
        cv2.waitKey(1)
        cv2.setMouseCallback(self.win_name, self.onMouse)
        cv2.imshow(self.win_name, self.img)
        cv2.waitKey(1)

        while self.count is not 4:
            cv2.waitKey(100)

        self.exit()



    def onMouse(self, event, x,y, flags, params):
        #print event, "%d,%d" %(x,y)
        if event == cv2.EVENT_LBUTTONDOWN:
            self.stash(x,y)

    def stash(self, x,y):
        cv2.circle(self.img, (x,y), 3, (0,255,0))
        self.showImage()

        self.click_data[self.count] = (x,y)
        self.count += 1
        if self.count >= 4:
            #self.count = 0
            self.exit()
        #print "click data:", self.click_data

    def exit(self):
        #cv2.setMouseCallback(self.win_name, None)
        cv2.destroyWindow(self.win_name)
        cv2.waitKey(1)

    '''def pushImage(self, img):
        self.img0 = img
        self.img = img.copy()
        self.showImage()'''

    def showImage(self):
        cv2.imshow(self.win_name, self.img)
        cv2.waitKey(1)


""" See https://gist.github.com/varhub/31384c6721e04d9d9210 """
def calculePerspectiveTransform(pO, pD):
    n = pO.shape[0]
    assert pO.shape == pD.shape
    assert n >= 4

    A = np.zeros((2*n,9))
    for i in range(0,n):
        (x1,y1) = (pO[i][0], pO[i][1])
        (x2,y2) = (pD[i][0], pD[i][1])

        A[2*i  ] = [x1,y1,1, 0, 0, 0, -x2*x1, -x2*y1, -x2]
        A[2*i+1] = [0, 0, 0, x1,y1,1, -y2*x1, -y2*y1, -y2]

    U,S,V = np.linalg.svd(A)
    H = V[-1].reshape((3,3))
    H = H/H[2,2]

    return H