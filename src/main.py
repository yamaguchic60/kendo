from detection import CameraTracker
# from move import *

import time

tracker = CameraTracker()
tracker.find_camera_device()
tracker.setup_camera()
start_time=time.time()

while 1:
    print(tracker.track_when_it_called())
tracker.release_resources()