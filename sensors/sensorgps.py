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
#       Alberto Martin Florido <almartinflorido@gmail.com>
#
import sys, traceback, Ice
import jderobot
import threading


class SensorGPS:

    def __init__(self):
        self.lock = threading.Lock()
        self.loggps = open('gps.log', 'w')

        try:
            ic = Ice.initialize(sys.argv)
            properties = ic.getProperties()

            basepose3D = ic.propertyToProxy("Introrob.Pose3D.Proxy")
            self.pose3DProxy=jderobot.Pose3DPrx.checkedCast(basepose3D)
            if self.pose3DProxy:
                self.pose=jderobot.Pose3DData()
            else:
                print 'Interface pose3D not connected'

            # basenavdatagps = ic.propertyToProxy("Introrob.NavdataGPS.Proxy")
            # print basenavdatagps,type(basenavdatagps)
            # self.navdataGPSProxy=jderobot.NavdataGPSPrx.checkedCast(basenavdatagps)
            # if self.navdataGPSProxy:
            #     self.gpsdata=self.navdataGPSProxy.getNavdataGPS()
            # else:
            #     print 'Interface NavdataGPS not connected'

        except:
            traceback.print_exc()
            status = 1

    def __delete__(self, instance):
        print 'close loggps'
        self.loggps.close()

    def update(self):
        self.lock.acquire()
        # self.updateNavdataGPS()
        self.updatePose()
        self.lock.release()

        # self.loggps.write(str(self.gpsdata))
        strpose = 'pose3D (%f %f %f)' %(self.pose.x,self.pose.y,self.pose.z)
        self.loggps.write(strpose)
        #
        #
        # print 'gps_on:',self.gpsdata.isGpsPlugged, 'firmwareStatus', self.gpsdata.firmwareStatus
        # print 'nbsat:',self.gpsdata.nbsat, 'gpsState', self.gpsdata.gpsState
        # print 'gps:',self.gpsdata.latitude, self.gpsdata.longitude, self.gpsdata.elevation
        # print 'gps0:',self.gpsdata.lat0, self.gpsdata.long0, self.gpsdata.latFused, self.gpsdata.longFused
        # print 'dataAvailable', self.gpsdata.dataAvailable, 'zeroValidated', self.gpsdata.zeroValidated
        # print 'lastFrameTimestamp', self.gpsdata.lastFrameTimestamp
        # print
        # print strpose
        # print


    def updatePose(self):
        if self.pose3DProxy:
            self.pose=self.pose3DProxy.getPose3DData()
            print self.pose

    def updateNavdataGPS(self):
        if self.navdataGPSProxy:
            self.gpsdata=self.navdataGPSProxy.getNavdataGPS()

    
    def getPose3D(self):
        if self.pose3DProxy:
            self.lock.acquire()
            tmp=self.pose
            self.lock.release()
            return tmp

        return None
    
