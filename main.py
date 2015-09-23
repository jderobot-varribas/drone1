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


from sensors.sensor import Sensor
from MyAlgorithm import MyAlgorithm
from periodic_thread import PeriodicThread
import sys

USE_GUI = True
if "--no-gui" in sys.argv:
    USE_GUI=False

if USE_GUI:
    from gui import minimal_gui, qtimshow
    from PyQt4 import QtGui
    import sys

if __name__ == '__main__':
    sensor = Sensor()
    t1 = PeriodicThread(0.025, sensor.update)
    t1.setDaemon(True)
    t1.start()

    algorithm = MyAlgorithm(sensor)
    t2 = PeriodicThread(0.033, algorithm.execute)
    t2.setDaemon(True)
    t2.start()

    if USE_GUI:
        app = QtGui.QApplication(sys.argv)
        #imageDisplay = minimal_gui.ImgDisplay()
        qtimshow.enable()
        #algorithm.debugImg = lambda(img): imageDisplay.Q_SIGNAL_ImageUpdate.emit(img)
        #qtimshow.disable()

        app.exec_()
    else:
        t2.join()

