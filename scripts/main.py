import threading
import time
import queue
from detection import CameraTracker
from move import RobotController
import time
import matplotlib.pyplot as plt
from get import start_udp_thread, get_position
from trajectory import (
    point_generation,
    setup_plot,
    update_plot,
    mo_x, mo_y, mo_z,  # 軌跡リスト（必要なら参照する）
    # get_position       # データ取得関数（StopIteration を検知したい場合など）
)

global flag=False

# def func1(output_queue):
#     # from detection
#     tracker = CameraTracker()
#     tracker.find_camera_device()
#     tracker.setup_camera()
#     start_time=time.time()
#     previous_time=start_time
#     #default value
#     max_qsize = 1
#     """1000Hzで動作し、結果をキューに送る関数"""
#     while True:
#         y,z,_1,_2 = y,z,_1,_2=tracker.track_when_it_called()#return red position
#         # print(f"func1 produced: {y,z}")
#         print(f"output_queue.qsize():{output_queue.qsize()}")
#         if output_queue.qsize() < max_qsize:
#             output_queue.put((y,z))  # 結果をキューに追加
#         #print delay
#         # print(f'func1 delay:{1000*(time.time()-previous_time)}ms')
#         previous_time=time.time()

def func1(output_queue):
    time.sleep(5)#waiting for initializing robot position
    start_udp_thread(host='10.216.71.90', port=50006)
    #default value
    max_qsize = 1
    # 1. 軌跡データを生成
    #  最終的には要らない
    # point_generation()

    # 2. プロット初期化
    (fig, ax_3d, ax_2d,
     trajectory_3d, meet_point_3d, dummy_s, dummy_t, frame_text, meet_point_text,
     observed_points, conic_curve, conic_curve_2, meet_point_2d,
     eq_text_2d, meet_point_3d_text) = setup_plot()

    # 3. while文でロボット制御 + アニメーション更新
    time_step = 0
    """1000Hzで動作し、結果をキューに送る関数"""
    while True:
        try:
            # (x,y,z) データを受け取る。
            # 最終的にはdetection.pyで行う処理
            x_in, y_in, z_in = get_position(skip_rate=10, timeout=0.05)
            if x_in<2.0:
                flag=True           
            else:
                continue
            # 目標点＋アニメーションの更新          
            target_x, target_y, target_z = update_plot(
                x_in, y_in, z_in,
                time_step,
                ax_3d, ax_2d,
                trajectory_3d, meet_point_3d, frame_text, meet_point_text,
                observed_points, conic_curve, conic_curve_2, meet_point_2d,
                eq_text_2d, meet_point_3d_text
            )
            time_step += 1

            # Matplotlib の描画を手動で更新
            plt.pause(0.01)
            # print(f"func1 produced: {y,z}")
            print(f"output_queue.qsize():{output_queue.qsize()}")
            if output_queue.qsize() < max_qsize:
                output_queue.put((target_y,target_z))  # 結果をキューに追加
        except StopIteration:
            print("全ての点を取得し終わりました。ループを終了します。")
            time.sleep(10)
            exit()

    



def func2(input_queue):
    # from move
    robot_controller = RobotController(robot_num=3)
    robot_controller.initialize_position()
    """10Hzで動作し、func1の返り値を処理する関数"""
    # _waiting_for_collecting_sword_point_data=10
    cnt=0
    while flag!=True:
        try:
            # print(f'input_queue.qsize():{input_queue.qsize()}')
            # キューからデータを取得
            data = input_queue.get() 
            # print(f"func2 consumed: {data}")
            previous_y,previous_z = data
            y,z=-previous_z,previous_y
            z+=0.5
            print(y,z)
            target_position = [y,z]#YOU can change this value!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            print(f'real_world y,z:{y,z}')
            cnt+=1
            # if cnt<_waiting_for_collecting_sword_point_data:
            #     continue
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
