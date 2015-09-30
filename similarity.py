# Copyright (c) 2015
# Author: Victor Arribas <v.arribas.urjc@gmail.com>
# Domain: Master Vision Artificial, URJC
# License: GPLv3 <http://www.gnu.org/licenses/gpl-3.0.html>

"""
compute similarity
same as https://bitbucket.org/masterva-varribas/rob-p2-jderobot/src/master/correspondence.h

options:
http://stackoverflow.com/questions/6991471/computing-cross-correlation-function
https://docs.scipy.org/doc/numpy/reference/generated/numpy.correlate.html
https://docs.scipy.org/doc/scipy-0.15.1/reference/generated/scipy.signal.correlate2d.html
https://docs.scipy.org/doc/numpy/reference/generated/numpy.dot.html
https://docs.scipy.org/doc/numpy/reference/generated/numpy.vdot.html
https://docs.scipy.org/doc/numpy/reference/generated/numpy.tensordot.html
"""

import cv2
import numpy as np
import operator
import functools


""" cross-correlation
Float casting is mandatory to avoid value overflow
with vdot for flat n-dimensinal arrays
"""
def correlation(a,b):
    a = np.asarray(a, np.float32)
    b = np.asarray(b, np.float32)

    a -= a.mean()
    b -= b.mean()

    aa = np.vdot(a,a)
    bb = np.vdot(b,b)
    ab = np.vdot(a,b)

    value = ab / np.sqrt(aa*bb)

    return value


""" Sum of Squared Differences
Float casting is mandatory due to negative values
remember that most common matrix are of uint8
Notice that it works for any array (N-dimension)
"""
def ssd(a, b):
    aa = np.asarray(a, np.float32)
    bb = np.asarray(b, np.float32)

    dd = aa-bb;
    value = np.vdot(dd,dd)
    return value

""" Inverted SSD.
Best value is biggest (up to 1).
"""
def ssd_inv(a,b):
    return 1/(1+ssd(a,b))


""" Normalized Inverted SSD.
use reduce to obtain N-ary shape area
http://stackoverflow.com/questions/13840379/python-multiply-all-items-in-a-list-together
"""
def ssd_norm_inv(a,b):
    area = functools.reduce(operator.mul, a.shape)
    if (area < 1):
        return -1
    ratio = ssd(a,b) / area
    return 1/(1+ratio)

""" normalized using current template shape
and major template shape. Trick for compare
cropped templates"""
def ssd_norm2_inv(a,b, shape):
    area = functools.reduce(operator.mul, a.shape)
    if area < 1:
        return -1
    area2 = functools.reduce(operator.mul, shape)
    ratio = ssd(a,b) * area2 / (area*area)
    return 1/(1+ratio)