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



from PyQt4.QtGui import QImage
import numpy as np
__Qimshow = None

def qimshow(img, title="imshow", format=QtGui.QImage.Format_RGB888):
    if __Qimshow is not None:
        __Qimshow.Q_SIGNAL_imshow.emit(img, title, format)


def enable_qimshow(self):
    global __Qimshow
    __Qimshow = Qimshow()



class Qimshow(QtCore.QObject):

    Q_SIGNAL_imshow = QtCore.pyqtSignal(np.ndarray, str, int)

    def __init__(self):
        QtCore.QObject.__init__(self)
        self.Q_SIGNAL_imshow.connect(self._qimshow)

    @QtCore.pyqtSlot(np.ndarray, str, int)
    def _qimshow(self, img, title="imshow", format=QtGui.QImage.Format_RGB888):
        if len(img.shape) == 3:
            qimg = QtGui.QImage(img.data, img.shape[1], img.shape[0], img.shape[1]*img.shape[2], format);
        else:
            qimg = QtGui.QImage(img.data, img.shape[1], img.shape[0], img.shape[1], format);
        WinSize = QtCore.QSize(img.shape[1],img.shape[0])

        qui_win = self._fetchWin(title)
        if qui_win is None:
            qui_win = QtGui.QWidget()
            qui_win.setWindowTitle(title)
            qui_win.resize(WinSize)

            qui_imgLabel = QtGui.QLabel(qui_win)
            qui_imgLabel.move(0,0);
            qui_imgLabel.resize(WinSize)
            qui_imgLabel.show()

            qui_win.setVisible(True)

            self._addWin(qui_win)

        qui_imgLabel = qui_win.children()[0]
        qui_imgLabel.setPixmap(QtGui.QPixmap.fromImage(qimg))

        return qui_win


    __win_list = []

    def _addWin(self, win):
        if win not in self.__win_list:
            self.__win_list.append(win)

    def _fetchWin(self, title):
        for win in self.__win_list:
            if title == win.windowTitle():
                return win
        return None