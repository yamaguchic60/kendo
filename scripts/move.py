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
    def test_run_when_it_is_called(self):
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

    def run_when_it_is_called(self, target_pose):
        """
        逆運動学を利用してロボットを目標位置に移動させるメソッド。
        :param target_pose: [x, y, z, rx, ry, rz] の形式の目標ポーズ（ロボットのエンドエフェクタ位置と回転）。
        """
        try:
            # 現在のエンドエフェクタ位置を取得
            current_pose = self.rtde_r.getActualTCPPose()
            print(f"Current TCP Pose: {current_pose}")

            # 目標ポーズを受け取り、逆運動学を計算
            joint_positions = self.rtde_c.getInverseKinematics(target_pose)
            if joint_positions:
                print(f"Calculated Joint Positions: {joint_positions}")
                # 計算されたジョイント位置に移動
                self.rtde_c.moveJ(joint_positions, self.acceleration, self.time_duration)
            else:
                print("Inverse Kinematics calculation failed.")
        except Exception as e:
            print(f"Error in run_when_it_is_called: {e}")





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
    while 1:        
        try:
            robot_controller.run_when_it_is_called()
        except KeyboardInterrupt:
            break
    robot_controller.cleanup()