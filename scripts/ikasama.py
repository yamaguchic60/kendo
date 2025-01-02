import rtde_control
import rtde_receive
import time
import random
import math
import numpy as np
#set your wired network as below.
# ip_address=10.216.71.90,
# netmask=255.255.0.0,
# gateway=None.

#set parameter here
#3:ur3e,10:ur10e
robot_num=3

#default values
ip_address={}
ip_address[3]='10.216.71.93'
ip_address[10]='10.216.71.92'
# ロボットのIPアドレスを指定
ROBOT_IP = ip_address[robot_num]
print(f'robot_ip:{ROBOT_IP}')


# RTDEコントロールとRTDEレシーブのインスタンスを作成
rtde_c = rtde_control.RTDEControlInterface(ROBOT_IP)
rtde_r = rtde_receive.RTDEReceiveInterface(ROBOT_IP)
joint_angle=[0.0, -1.57, 0.0, -1.57, 0.0, 1.57]
#joint_angular_velocity=[0.0,0.0,0.0,0.0,0.0,0.0]
#joint_angle[0] is the base joint, and joint_angle[5] is the hand.
#set robot to start position
print('initialize position')
rtde_c.moveJ(joint_angle)
print('control start')
def initialize():
    joint_angle=[0.0, -1.57, 0.0, -1.57, 0.0, 1.57]
    rtde_c.moveJ(joint_angle)
    print('control start')
    start_time=time.time()
    return start_time
start_time = time.time()
try:
    while True:
        if time.time()-start_time>10:
            start_time=initialize()
        # 目標ジョイント位置に移動
        theta1=-math.pi/4+np.random.uniform(-0.1,0.1)
        theta2=math.pi*5/4+np.random.uniform(-0.1,0.1)
        joint_angle = [0.0, -math.pi / 2+theta1, 0.0, -math.pi / 2, 0.0, theta2]
        rtde_c.moveJ(joint_angle)

        # 現在のジョイント位置を取得して表示
        current_joint_positions = rtde_r.getActualQ()
        print("Current joint positions: ", current_joint_positions)
        #randomize joint_angle[5]
        joint_angle[5]=30#random.uniform(-1,1)
        print('randomized joint[5]')

except KeyboardInterrupt:
    pass

# RTDEコントロールとRTDEレシーブのインスタンスを停止
rtde_c.stopScript()
rtde_r.disconnect()