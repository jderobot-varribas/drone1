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

from PyQt4 import QtGui, QtCore
import numpy as np


class ImgDisplay(QtGui.QMainWindow):

    WinSize = QtCore.QSize(64,32)

    ## Declare a Qt Signal for message passing
    Q_SIGNAL_ImageUpdate = QtCore.pyqtSignal(np.ndarray);

    def __init__(self):
        QtGui.QMainWindow.__init__(self)

        ## Register SIGNAL receiver
        self.Q_SIGNAL_ImageUpdate.connect(self.updateImage)

        ## UI Stuff
        self.setWindowTitle("Image Display")
        self.setVisible(True)
        self.qui_imgLabel = QtGui.QLabel(self)
        self.qui_imgLabel.move(0,0);
        self.qui_imgLabel.resize(self.WinSize)
        self.qui_imgLabel.show()


    @QtCore.pyqtSlot(np.ndarray)
    def updateImage(self, img):
        #print "SIGNAL arg type" +str(type(img))

        self.WinSize=QtCore.QSize(img.shape[1],img.shape[0])
        self.resize(self.WinSize);
        self.qui_imgLabel.resize(self.WinSize)

        qimg = QtGui.QImage(img.data, img.shape[1], img.shape[0], img.shape[1]*img.shape[2], QtGui.QImage.Format_RGB888);
        self.qui_imgLabel.setPixmap(QtGui.QPixmap.fromImage(qimg))



