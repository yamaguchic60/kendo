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
    x,y,_1,_2=tracker.track_when_it_called()#return red position
    try:

        target_position = [0.4+x/10000,0.3+y/10000]
        print(x,y)
        robot_controller.run_when_it_is_called(target_position)#control robot

    except KeyboardInterrupt:
        break

#finish
print("Stopping the RTDE interface.")
robot_controller.cleanup()
tracker.release_resources()