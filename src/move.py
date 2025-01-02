import rtde_control
import rtde_receive
import time
import math
import random

# ロボットの初期設定
robot_num = 3
acceleration = 0.5
time_duration = 0.01
ip_address = {3: '10.216.71.93', 10: '10.216.71.92'}
ROBOT_IP = ip_address[robot_num]

# RTDEコントロールとRTDEレシーブのインスタンスを作成
rtde_c = rtde_control.RTDEControlInterface(ROBOT_IP)
rtde_r = rtde_receive.RTDEReceiveInterface(ROBOT_IP)
thresh_hold=0.1# ジョイントの動作範囲を設定(this is for debug,if you complete,you set this value to 1 or delete this.)
joint_limits = {
    0: (-0*thresh_hold * math.pi, 0*thresh_hold * math.pi),  # ベース
    1: (-thresh_hold * math.pi-math.pi/2, thresh_hold * math.pi-math.pi/2),  # ショルダー
    2: (-thresh_hold * math.pi, thresh_hold * math.pi),  # エルボー
    3: (-thresh_hold*math.pi-math.pi/2, thresh_hold*math.pi-math.pi/2),  # リスト1
    4: (-math.pi, math.pi),  # リスト2
    5: (-math.inf, math.inf)  # リスト3 (範囲を指定)
}

# 初期位置
joint_angle = [0.0, -math.pi / 2, 0.0, -math.pi / 2, 0.0, 0.0]
print(f'initialize the angular position to {joint_angle}')
rtde_c.moveJ(joint_angle)
print(f'control start')


try:
    while True:
        # 現在のジョイント位置を取得
        current_joint_positions = rtde_r.getActualQ()
        
        # ランダムな速度を生成
        joint_angular_velocity = [
            random.uniform(-math.pi / 2, math.pi / 2) for _ in range(6)
        ]  # ランダムな速度を生成 (-90°/s ~ +90°/s)

        # 1秒後の予測位置を計算
        next_positions = [
            current_joint_positions[i] + joint_angular_velocity[i] * time_duration
            for i in range(6)
        ]
        
        # 動作範囲を超えないように調整
        for i in range(6):
            if next_positions[i] < joint_limits[i][0] or next_positions[i] > joint_limits[i][1]:
                joint_angular_velocity[i] = 0.0  # 制限に達した場合速度をゼロに設定

        # 修正した速度でロボットを制御
        print(f"Random joint velocities (adjusted): {joint_angular_velocity}")
        print(f"Next positions (clamped): {next_positions}")
        rtde_c.speedJ(joint_angular_velocity, acceleration, time_duration)

        # 現在のジョイント位置を表示
        for i in range(len(current_joint_positions)):
            print(f'joint{i}:',current_joint_positions[i])

        # print("Current joint positions: ", current_joint_positions)
        time.sleep(1)

except KeyboardInterrupt:
    pass
finally:
    # RTDEインターフェースを停止
    rtde_c.stopScript()
    rtde_r.disconnect()
