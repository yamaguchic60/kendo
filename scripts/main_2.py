import time
import matplotlib.pyplot as plt

from trajectory import (
    point_generation,
    setup_plot,
    update_plot,
    mo_x, mo_y, mo_z,  # 軌跡リスト（必要なら参照する）
    get_position       # データ取得関数（StopIteration を検知したい場合など）
)

def move_arm(x, y, z):
    """
    他の開発者が優先度高く実装予定のロボットアーム制御関数。
    ここではダミーとして print と短い sleep だけ。
    """
    print(f"Moving robot arm to ({x:.3f}, {y:.3f}, {z:.3f})")
    # time.sleep(0.01)

def main():
    # 1. 軌跡データを生成
    #  最終的には要らない
    point_generation()

    # 2. プロット初期化
    (fig, ax_3d, ax_2d,
     trajectory_3d, meet_point_3d, dummy_s, dummy_t, frame_text, meet_point_text,
     observed_points, conic_curve, conic_curve_2, meet_point_2d,
     eq_text_2d, meet_point_3d_text) = setup_plot()

    # 3. while文でロボット制御 + アニメーション更新
    time_step = 0
    while True:
        try:
            # (x,y,z) データを受け取る。
            # 最終的にはdetection.pyで行う処理
            x_in, y_in, z_in = get_position(time_step)           

            # 目標点＋アニメーションの更新          
            target_x, target_y, target_z = update_plot(
                x_in, y_in, z_in,
                time_step,
                ax_3d, ax_2d,
                trajectory_3d, meet_point_3d, frame_text, meet_point_text,
                observed_points, conic_curve, conic_curve_2, meet_point_2d,
                eq_text_2d, meet_point_3d_text
            )
            
            # ロボットアームを動かす。
            # 最終的にはmove.pyでする
            move_arm(target_x, target_y, target_z)

            time_step += 1

            # Matplotlib の描画を手動で更新
            plt.pause(0.01)

        except StopIteration:
            print("全ての点を取得し終わりました。ループを終了します。")
            break

    # グラフを表示したままにする場合
    plt.show()

if __name__ == "__main__":
    main()
