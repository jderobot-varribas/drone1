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
#


import numpy as np
import cv2

import similarity

from gui.qtimshow import imshow

""" Image is a PNG, so load it as BGRA to catch alpha channel
Then, extract Alpha channel for maskerading purposes,
and finally convert to JdeRobot RGB format.
"""
_USE_ALPHA_CHANNEL_ = False
_IMAGE_PATH = "marks/arrow_mark.png"

_IMAGE_REF = cv2.imread(_IMAGE_PATH, cv2.CV_LOAD_IMAGE_UNCHANGED)
if _IMAGE_REF.shape[2] == 4:
    _IMAGE_REF_ALPHA = _IMAGE_REF[:,:, 3].copy() # copy is neede to obtain a non sparse matrix
    _IMAGE_REF = cv2.cvtColor(_IMAGE_REF, cv2.COLOR_BGRA2RGB)
    if not _USE_ALPHA_CHANNEL_:
        """ OpenCV converts alpha to back, there are 2 ways to do this:
         a) by use bit operators (deprecated)
         b) by set transparent pixels to white
         """
        _IMAGE_REF[_IMAGE_REF_ALPHA==0] = (255,255,255)
        #_IMAGE_REF_ALPHA = np.dstack( (_IMAGE_REF_ALPHA,_IMAGE_REF_ALPHA,_IMAGE_REF_ALPHA))
        #cv2.bitwise_not(_IMAGE_REF, _IMAGE_REF)
        #cv2.bitwise_xor(_IMAGE_REF, _IMAGE_REF_ALPHA, _IMAGE_REF)
        _IMAGE_REF_ALPHA = None
else:
    _IMAGE_REF_ALPHA = None
    _IMAGE_REF = cv2.cvtColor(_IMAGE_REF, cv2.COLOR_BGR2RGB)
print "Detection with alpha channel: ", _USE_ALPHA_CHANNEL_

if _IMAGE_REF is None:
    msg = 'detection init fail: mark "%s" was not found.' %(_IMAGE_PATH)
    raise Exception(msg)


""" Ugly way of create a enum.
enums are native supported since python 3.4, but see this [1] to gt full idea
and custom ways to accomplish it
[1] http://stackoverflow.com/questions/36932/how-can-i-represent-an-enum-in-python
"""
class MarkType:
    RIGHT=0
    LEFT=2
    UP=1
    DOWN=3

    types=[RIGHT,UP,LEFT,DOWN]
    names=['RIGHT','UP','LEFT','DOWN']


def mark_direction(img):
    (height, width) = img.shape[0:2];
    ref = cv2.resize(_IMAGE_REF, (width, height))
    if _IMAGE_REF_ALPHA is not None:
        mask = cv2.resize(_IMAGE_REF_ALPHA, (width, height))
        mask = np.dstack((mask,mask,mask))

    scores = []
    for mt in MarkType.types:
        rot90x = cv2.getRotationMatrix2D((width/2.0, height/2.0), mt*90, 1)
        _ref = cv2.warpAffine(ref, rot90x, (width, height))

        if _IMAGE_REF_ALPHA is not None:
            _mask = cv2.warpAffine(mask, rot90x, (width, height))
            _img = cv2.bitwise_and(_mask, img)
        else:
            _img = img

        score = similarity.correlation(_ref, _img)
        scores.append(score)

        #imshow('ref[%s]'%(MarkType.names[mt]), _ref.copy())

    indx = np.argmax(scores)
    print 'best score: ', MarkType.names[indx], indx, scores
    return MarkType.types[indx], scores[indx]