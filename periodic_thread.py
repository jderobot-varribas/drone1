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

import threading
import signal
import time

# Enable exit with Ctrl+C
signal.signal(signal.SIGINT, signal.SIG_DFL)


class PeriodicThread(threading.Thread):

    def __init__(self, secs=1, fn=None):
        threading.Thread.__init__(self)
        self.periodic_wait = secs
        if fn is not None:
            self.periodic_run = fn

    def run(self):
        while True:
            start_time = time.time()

            self.periodic_run()

            finish_time = time.time()
            dt = finish_time - start_time;

            to_wait = self.periodic_wait - dt;
            if to_wait > 0:
                time.sleep(to_wait)

    def periodic_run(self): pass
