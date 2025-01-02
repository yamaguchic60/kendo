import threading
import time
import queue
from detection import CameraTracker
from move import RobotController
import time

def func1(output_queue):
    # from detection
    tracker = CameraTracker()
    tracker.find_camera_device()
    tracker.setup_camera()
    start_time=time.time()
    previous_time=start_time
    #default value
    max_qsize = 1
    """1000Hzで動作し、結果をキューに送る関数"""
    while True:
        y,z,_1,_2 = y,z,_1,_2=tracker.track_when_it_called()#return red position
        # print(f"func1 produced: {y,z}")
        print(f"output_queue.qsize():{output_queue.qsize()}")
        if output_queue.qsize() < max_qsize:
            output_queue.put((y,z))  # 結果をキューに追加
        #print delay
        # print(f'func1 delay:{1000*(time.time()-previous_time)}ms')
        previous_time=time.time()

def func2(input_queue):
    # from move
    robot_controller = RobotController(robot_num=3)
    robot_controller.initialize_position()
    """10Hzで動作し、func1の返り値を処理する関数"""
    while True:
        try:
            # print(f'input_queue.qsize():{input_queue.qsize()}')
            # キューからデータを取得
            data = input_queue.get() 
            # print(f"func2 consumed: {data}")
            y,z = data
            target_position = [0.4+y/10000,0.3+z/10000]#YOU can change this value!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            print(y,z)
            robot_controller.run_when_it_is_called(target_position)#control robot
        except queue.Empty:
            # キューが空の場合はスキップ
            continue

def main():
    # スレッド間でデータを共有するキュー
    shared_queue = queue.Queue()

    # func1を別スレッドで実行
    thread_func1 = threading.Thread(target=func1, args=(shared_queue,))
    thread_func1.daemon = True
    thread_func1.start()

    # func2を別スレッドで実行
    thread_func2 = threading.Thread(target=func2, args=(shared_queue,))
    thread_func2.daemon = True
    thread_func2.start()

    # メインスレッドを終了しないように無限ループ
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
