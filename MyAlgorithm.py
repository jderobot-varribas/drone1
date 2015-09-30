import math
import jderobot
import cv2
import numpy as np
import rectification
import detection
from gui.qtimshow import imshow

import adrian_rosebrock


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

            '''
            HSV_GY_low = (28,10,0)
            HSV_GY_upp = (64,255,255)

            hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
            mask = cv2.inRange(hsv, HSV_GY_low, HSV_GY_upp)
            img_out = cv2.bitwise_and(img, img, mask=mask)

            imshow("mask", mask)
            imshow("filtered", img_out)
            '''

            # Mark detection
            #detect1(img)
            #detect2(img)
            marks = detect3(img, False)

            img_highlight = img.copy()
            for mark_center, mark_rect in marks:
                ref_rect = adrian_rosebrock.rect_target_size(mark_rect)
                tf = rectification.calculePerspectiveTransform(mark_rect, ref_rect)
                img_rect = cv2.warpPerspective(img, tf, tuple(ref_rect[2]+1))

                direction, score = detection.mark_direction(img_rect)
                text1 = detection.MarkType.names[direction]
                text2 = "%.2f" %(score)
                cv2.putText(img_highlight, text1, tuple(mark_center), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200,100,255), 2)
                cv2.putText(img_highlight, text2, tuple(mark_center+(0,12)), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200,100,255), 2)

            imshow("recognized", img_highlight)


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


## Yellow corners
HSV_Y_low = (27,140, 50)
HSV_Y_upp = (33,255,150)

def detect2(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    mask = cv2.inRange(hsv, HSV_Y_low, HSV_Y_upp)
    imshow("d2:mask", mask.astype(np.uint8))

    ''' median blur to drop salt noise
    dilate op. to avoidmedian cutoff '''
    k_cross = cv2.getStructuringElement(cv2.MORPH_CROSS, (3,3))
    mask = cv2.dilate(mask, k_cross)
    imshow("d2:dilate", mask)
    mask = cv2.medianBlur(mask, 3)
    imshow("d2:median", mask)

    img_poly = img.copy()

    detected_corners = []
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        ''' center from perimeter '''
        m = cv2.moments(contour)
        m00 = m['m00']
        if m00 > 0:
            cx = int(m['m10']/m00)
            cy = int(m['m01']/m00)
            cv2.circle(img_poly, (cx,cy), 3, (0,0,255), -1)
            detected_corners.append( (cx,cy) )
    imshow("d2:yellow corners", img_poly)

    ''' group marks '''
    print 'yellow corners detected:', len(detected_corners)
    if len(detected_corners) >= 4:
        take4 = detected_corners[0:4]
        ''' sort it
        use (0,0) distance to known tl and br points'''
        tld = np.Inf
        brd = 0
        img_poly = img_poly.copy()
        for point in take4:
            cv2.circle(img_poly, point, 3, (255,0,0), -1)
            d = np.linalg.norm(point)
            if d<tld:
                tld=d,
                tl=point
            if d>brd:
                brd=d
                br=point
        take4.remove(tl)
        take4.remove(br)

        cv2.line(img_poly, tl, br, (0,255,255))
        imshow("d2:points", img_poly)

        ''' use cross-product to detect side position '''
        for pt in take4:
            v1 = (br[0]-tl[0], br[1]-tl[1], 0)
            v2 = (pt[0]-tl[0], pt[1]-tl[1], 0)
            sign = np.cross(v1,v2)[2]
            if sign < 0:
                ne=pt
            else:
                po=pt

        return
        """ ne or po can be undefined. This is due:
        1) 4 selected points could be bad (impossible configuration)
        2) distance to (0,0) is not 100% stable to perspective nor rotations (like roll)
        """

        sorted = np.array([ tl, po, br, ne ])
        ref = np.array([ (0,0), (0,100), (100,100), (100,0) ])

        tf = rectification.calculePerspectiveTransform(sorted, ref)
        img_rect = cv2.warpPerspective(img, tf, (100,100))

        imshow("d2:rectified", img_rect)


YELLOW_SEARCH_AREA_RATIO = 1.25 # it should not be a constant, but an 'aperture angle based' function

def detect3(img, debug=True):
    mark_list = detectGreenArrows(img)
    if len(mark_list) == 0:
        return []

    if debug:
        draw = img.copy()
        for mark in mark_list:
            cv2.drawContours(draw, [mark[2]], -1, (255,0,255))
            cv2.circle(draw, mark[0], 2, (255,255,255), -1)

            (x,y,w,h) = mark[1]
            cv2.rectangle(draw, (x,y), (x+w,y+h), (100,100,100))
            r = int(max(w,h)*YELLOW_SEARCH_AREA_RATIO)
            cv2.circle(draw, mark[0], r, (255,255,255), 1)
        imshow('d3: detectGreenArrows', draw)

    corners_list = np.asarray(detectYellowCorners(img))
    if len(corners_list) == 0:
        return []

    ''' marriage problem'''
    marks_out = []
    count=0
    for mark in mark_list:
        count+=1; #print 'mark[%d]'%(count)
        center = np.asarray(mark[0])
        radius = max(mark[1][2], mark[1][3])
        radius = np.ceil(radius*YELLOW_SEARCH_AREA_RATIO)

        diff = corners_list - center
        dist = np.linalg.norm(diff, axis=1)
        condition = dist < radius
        passing = corners_list[condition] # or condition.nonzero()

        #print 'passing corners:',len(passing)

        if debug:
            for point in passing:
                cv2.circle(draw, tuple(point), 2, (255,255,255), -1)
            imshow('d3: detectCorners', draw)

        if len(passing) >= 4:
            sorted = adrian_rosebrock.order_points(passing[0:4])
            scale=200
            ref = np.array([ (0,0), (1,0), (1,1), (0,1) ])*scale

            tf = rectification.calculePerspectiveTransform(sorted, ref)
            img_rect = cv2.warpPerspective(img, tf, (scale,scale))

            if debug:
                for point in passing:
                    cv2.circle(draw, tuple(point), 2, (255,255,255), -1)
                imshow('d3: mark[%d]'%(count), img_rect)

            marks_out.append( (center, sorted) )

    return marks_out


def detectGreenArrows(img):
    mark_list = [] # as (center, bounding box, contour)

    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    mask = cv2.inRange(hsv, HSV_G_low, HSV_G_upp)

    contours, hierarchy = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    for contour in contours:
        ''' center from perimeter '''
        m = cv2.moments(contour)
        m00 = m['m00']
        if m00 > 0:
            cx = int(m['m10']/m00)
            cy = int(m['m01']/m00)
            desc = ( (cx,cy), cv2.boundingRect(contour), contour )
            mark_list.append(desc)

    return mark_list


def detectYellowCorners(img):
    detected_corners = []

    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    mask = cv2.inRange(hsv, HSV_Y_low, HSV_Y_upp)

    ''' median blur to drop salt noise
    dilate op. to avoidmedian cutoff '''
    k_cross = cv2.getStructuringElement(cv2.MORPH_CROSS, (3,3))
    mask = cv2.dilate(mask, k_cross)
    mask = cv2.medianBlur(mask, 3)

    contours, hierarchy = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        m = cv2.moments(contour)
        m00 = m['m00']
        if m00 > 0:
            cx = int(m['m10']/m00)
            cy = int(m['m01']/m00)
            detected_corners.append( (cx,cy) )

    return detected_corners
