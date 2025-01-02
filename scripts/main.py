from detection import CameraTracker
from move import RobotController
import time

# from detection
tracker = CameraTracker()
tracker.find_camera_device()
tracker.setup_camera()
start_time=time.time()
# from move
robot_controller = RobotController(robot_num=3)
robot_controller.initialize_position()



#loop
while 1:
    print(tracker.track_when_it_called())#return red position
    try:
        robot_controller.run_when_it_is_called()#control robot
    except KeyboardInterrupt:
        break

robot_controller.cleanup()

tracker.release_resources()