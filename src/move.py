import rtde_control
import rtde_receive
import time
import math
import random


class RobotController:
    def __init__(self, robot_num, thresh_hold=0.1, acceleration=0.5, time_duration=0.01):
        # ロボットの初期設定
        self.ip_address = {3: '10.216.71.93', 10: '10.216.71.92'}
        self.ROBOT_IP = self.ip_address[robot_num]

        self.acceleration = acceleration
        self.time_duration = time_duration
        self.thresh_hold = thresh_hold

        # RTDEコントロールとRTDEレシーブのインスタンスを作成
        self.rtde_c = rtde_control.RTDEControlInterface(self.ROBOT_IP)
        self.rtde_r = rtde_receive.RTDEReceiveInterface(self.ROBOT_IP)

        # ジョイントの動作範囲
        self.joint_limits = {
            0: (-0 * self.thresh_hold * math.pi, 0 * self.thresh_hold * math.pi),
            1: (-self.thresh_hold * math.pi - math.pi / 2, self.thresh_hold * math.pi - math.pi / 2),
            2: (-self.thresh_hold * math.pi, self.thresh_hold * math.pi),
            3: (-self.thresh_hold * math.pi - math.pi / 2, self.thresh_hold * math.pi - math.pi / 2),
            4: (-math.pi, math.pi),
            5: (-math.inf, math.inf),
        }

    def initialize_position(self, joint_angle=None):
        if joint_angle is None:
            joint_angle = [0.0, -math.pi / 2, 0.0, -math.pi / 2, 0.0, 0.0]
        print(f'Initializing the angular position to {joint_angle}')
        self.rtde_c.moveJ(joint_angle)
        print('Control start')

    def run(self):
        try:
            while True:
                # 現在のジョイント位置を取得
                current_joint_positions = self.rtde_r.getActualQ()

                # ランダムな速度を生成
                joint_angular_velocity = [
                    random.uniform(-math.pi / 2, math.pi / 2) for _ in range(6)
                ]

                # 次の予測位置を計算
                next_positions = [
                    current_joint_positions[i] + joint_angular_velocity[i] * self.time_duration
                    for i in range(6)
                ]

                # 動作範囲を超えないように調整
                for i in range(6):
                    if next_positions[i] < self.joint_limits[i][0] or next_positions[i] > self.joint_limits[i][1]:
                        joint_angular_velocity[i] = 0.0  # 制限に達した場合、速度をゼロに設定

                # 修正した速度でロボットを制御
                print(f"Random joint velocities (adjusted): {joint_angular_velocity}")
                print(f"Next positions (clamped): {next_positions}")
                self.rtde_c.speedJ(joint_angular_velocity, self.acceleration, self.time_duration)

                # 現在のジョイント位置を表示
                for i in range(len(current_joint_positions)):
                    print(f'Joint {i}: {current_joint_positions[i]}')

                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            self.cleanup()

    def cleanup(self):
        print("Stopping the RTDE interface.")
        self.rtde_c.stopScript()
        self.rtde_r.disconnect()


if __name__ == "__main__":
    # ロボット番号を指定してインスタンスを作成
    robot_controller = RobotController(robot_num=3)
    
    # 初期位置を設定
    robot_controller.initialize_position()

    # 制御ループを実行
    robot_controller.run()
