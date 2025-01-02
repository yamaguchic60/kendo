import numpy as np
from scipy.linalg import svd
from scipy.optimize import fsolve
import matplotlib.pyplot as plt
from collections import deque

# ---------------------
# グローバル設定
# ---------------------
mo_x = deque(maxlen=100)
mo_y = deque(maxlen=100)
mo_z = deque(maxlen=100)

# 点群（最初に生成して使い回す）
generated_points = []

# 定数
xr = 3.0  # x=xr

# s,t の前回の解を保持
prev_s, prev_t = 0, 0

# 直近の MeetPoint
prev_x_mp = 3.0
prev_y_mp = 1.0
prev_z_mp = 1.0

# ---------------------
# 点生成＆取得まわり
# ---------------------
def point_generation():
    """条件に基づいて点を生成"""
    global generated_points
    t = np.linspace(0, 7.5, 90)
    x = t * 4 / 10
    y = x
    # z = x
    z = -x**2 + 4 * x

    noise_x = np.random.normal(0, 0.01, size=x.shape)
    noise_y = np.random.normal(0, 0.01, size=y.shape)
    noise_z = np.random.normal(0, 0.01, size=z.shape)

    x_noisy = x + noise_x
    y_noisy = y + noise_y
    z_noisy = z + noise_z

    generated_points = np.array([x_noisy, y_noisy, z_noisy]).T  # shape: (N, 3)

def get_position(time_step):
    """point_generationで生成された点を1つずつ返す"""
    global generated_points
    if time_step < len(generated_points):
        return generated_points[time_step]  # (x, y, z)
    else:
        raise StopIteration("全ての点を取得しました")

# ---------------------
# Conicまわり
# ---------------------
def get_conic_params(s, t):
    """
    Conic Modelのパラメータ [A, B, C, D, E, F] を計算し、F=1 に正規化
    As^2 + B*s*t + C*t^2 + D*s + E*t + F = 0
    """
    M = np.column_stack([s**2, s*t, t**2, s, t, np.ones_like(s)])
    _, _, Vt = svd(M, full_matrices=False)
    params = Vt[-1]
    
    # F=1 に正規化
    if abs(params[-1]) > 1e-12:
        params /= params[-1]
    else:
        norm_val = np.linalg.norm(params)
        if norm_val > 1e-12:
            params /= norm_val
    return params  # [A, B, C, D, E, F]

def solve_meet_point(params, xr, centroid, basis_s, basis_t):
    """
    連立方程式を fsolve で解く:
      1) A*s^2 + B*s*t + C*t^2 + D*s + E*t + F = 0 (Conic)
      2) xr = x0 + s*sx + t*tx
    """
    global prev_s, prev_t

    A, B, C, D, E, F = params
    x0 = centroid[0]
    sx = basis_s[0]
    tx = basis_t[0]

    def equations(vars):
        s, t = vars
        eq1 = A*s**2 + B*s*t + C*t**2 + D*s + E*t + F
        eq2 = (x0 + s*sx + t*tx) - xr
        return [eq1, eq2]

    s_init, t_init = prev_s, prev_t
    sol = fsolve(equations, [s_init, t_init])
    s_sol, t_sol = sol

    prev_s, prev_t = s_sol, t_sol
    return s_sol, t_sol

# ---------------------
# プロット初期化
# ---------------------
def setup_plot():
    """Figure, Axes, および描画要素をセットアップして返す"""
    fig = plt.figure(figsize=(12, 6))
    fig.suptitle("Solve MeetPoint with x=xr & Conic(s,t)=0")

    # 左: 3Dプロット
    ax_3d = fig.add_subplot(121, projection="3d")
    ax_3d.set_xlim(-1, 3)
    ax_3d.set_ylim(-4, 4)
    ax_3d.set_zlim(-4, -4)
    ax_3d.set_xlabel("X")
    ax_3d.set_ylabel("Y")
    ax_3d.set_zlabel("Z")

    trajectory_3d, = ax_3d.plot([], [], [], "b-", label="Trajectory")
    meet_point_3d, = ax_3d.plot([], [], [], "ro", label="MeetPoint", markersize=8)
    # ダミーのプロットを用いた quiver の凡例設定
    dummy_s, = ax_3d.plot([], [], [], color="magenta", label="Base S")  # Base S のダミー
    dummy_t, = ax_3d.plot([], [], [], color="cyan", label="Base T")  # Base T のダミー
    # フレーム数表示用のテキストを追加
    frame_text = ax_3d.text(0, 5, 6, "", color="black", fontsize=12)
    meet_point_text = ax_3d.text(0, 5, 5, "", color="red", fontsize=12)
    ax_3d.legend()

    # x=xr の面を可視化
    # Y, Z = np.meshgrid(np.linspace(0, 5, 11), np.linspace(0, 10, 11))
    # X = np.array([xr] * Y.shape[0])
    # ax_3d.plot_surface(X, Y, Z, alpha=0.3)

    # 右: 2Dプロット (s-t 平面)
    ax_2d = fig.add_subplot(122)
    ax_2d.set_xlim(-9, 9)
    ax_2d.set_ylim(-9, 9)
    ax_2d.set_xlabel("s")
    ax_2d.set_ylabel("t")
    observed_points, = ax_2d.plot([], [], "go", label="Observed Points")
    conic_curve, = ax_2d.plot([], [], "y--", label="Conic Curve")
    conic_curve_2, = ax_2d.plot([], [], "m--", label="Conic Curve 2")
    meet_point_2d, = ax_2d.plot([], [], "ro", label="MeetPoint")
    ax_2d.legend()

    # テキスト等
    # frame_text_3d = ax_3d.text(0, 5, 5.5, "", color="black", fontsize=12)
    eq_text_2d = ax_2d.text(-4.5, 4.5, "", fontsize=10, color="blue")
    meet_point_3d_text = ax_2d.text(-4.5, 5.5, "", fontsize=10, color="red")

    return (fig, ax_3d, ax_2d,
            trajectory_3d, meet_point_3d, dummy_s, dummy_t, frame_text, meet_point_text,
            observed_points, conic_curve, conic_curve_2, meet_point_2d,
            eq_text_2d, meet_point_3d_text)

# ---------------------
# 1フレームぶんの更新
# ---------------------
basis_s_quiver = None
basis_t_quiver = None

def update_plot(x_in, y_in, z_in, frame,
                ax_3d, ax_2d,
                trajectory_3d, meet_point_3d, frame_text, meet_point_text,
                observed_points, conic_curve, conic_curve_2, meet_point_2d,
                eq_text_2d, meet_point_3d_text):
    """frame番目のデータを使って Conic の更新 & プロットを行う"""

    global mo_x, mo_y, mo_z
    global basis_s_quiver, basis_t_quiver
    global prev_x_mp, prev_y_mp, prev_z_mp

    mo_x.append(x_in)
    mo_y.append(y_in)
    mo_z.append(z_in)

    # 2. 3D軌跡を更新
    trajectory_3d.set_data(mo_x, mo_y)
    trajectory_3d.set_3d_properties(mo_z)

    # 十分に点がたまるまでスキップ
    if len(mo_x) < 20:
        return prev_x_mp, prev_y_mp, prev_z_mp

    # 3. 平面の計算
    data = np.column_stack([mo_x, mo_y, mo_z])
    centroid = np.mean(data, axis=0)
    centered_data = data - centroid
    _, _, Vt = svd(centered_data)

    basis_s = Vt[0]
    basis_t = Vt[1]

    # 4. data を s-t 座標系に変換
    s_vals = np.dot(centered_data, basis_s)
    t_vals = np.dot(centered_data, basis_t)

    # 5. Conic Modelのパラメータを計算
    params = get_conic_params(s_vals, t_vals)

    # 6. MeetPoint の (s*, t*) を解く
    s_sol, t_sol = solve_meet_point(params, xr, centroid, basis_s, basis_t)

    # xyz に戻す
    x_mp = centroid[0] + s_sol*basis_s[0] + t_sol*basis_t[0]
    y_mp = centroid[1] + s_sol*basis_s[1] + t_sol*basis_t[1]
    z_mp = centroid[2] + s_sol*basis_s[2] + t_sol*basis_t[2]

    # 解が x=3±0.1 に入っていなければ前回の値を使う
    if -0.1 < x_mp < 0.1:
        verified_x_mp = x_mp
        verified_y_mp = y_mp
        verified_z_mp = z_mp
        prev_x_mp, prev_y_mp, prev_z_mp = x_mp, y_mp, z_mp
    else:
        verified_x_mp = prev_x_mp
        verified_y_mp = prev_y_mp
        verified_z_mp = prev_z_mp

    meet_point_3d.set_data([verified_x_mp], [verified_y_mp])
    meet_point_3d.set_3d_properties([verified_z_mp])

    # 基底ベクトルの矢印（quiver）を更新
    # 再描画前に remove しておく
    if basis_s_quiver is not None:
        basis_s_quiver.remove()
    if basis_t_quiver is not None:
        basis_t_quiver.remove()
    # 新たにプロット
    basis_s_quiver = ax_3d.quiver(*centroid, *basis_s, length=1.0, color="magenta")
    basis_t_quiver = ax_3d.quiver(*centroid, *basis_t, length=1.0, color="cyan")

    # 7. s-t 平面の更新
    observed_points.set_data(s_vals, t_vals)
    meet_point_2d.set_data([s_sol], [t_sol])

    # 8. Conic Curve を描画
    A, B, C, D, E, F = params
    t_lin = np.linspace(-9, 9, 300)
    s_curve_1, s_curve_2 = [], []
    t_curve_1, t_curve_2 = [], []
    for tv in t_lin:
        bs = B*tv + D
        cs = C*tv**2 + E*tv + F
        disc = bs**2 - 4*A*cs
        if disc >= 0 and abs(A) > 1e-12:
            sqrt_disc = np.sqrt(disc)
            s1 = (-bs + sqrt_disc) / (2*A)
            s2 = (-bs - sqrt_disc) / (2*A)
            s_curve_1.append(s1); t_curve_1.append(tv)
            s_curve_2.append(s2); t_curve_2.append(tv)
    conic_curve.set_data(s_curve_1, t_curve_1)
    conic_curve_2.set_data(s_curve_2, t_curve_2)

    # 9. テキスト表示
    eq_str = f"{A:.2f}s^2 + {B:.2f}st + {C:.2f}t^2 + {D:.2f}s + {E:.2f}t + {F:.2f} = 0"
    eq_text_2d.set_text(eq_str)
    # frame_text_3d.set_text(f"Frame: {frame}")
    meet_point_3d_text.set_text(f"({x_mp:.3f}, {y_mp:.3f}, {z_mp:.3f})")
        
    # 3Dグラフ内にフレーム数を表示
    frame_text.set_text(f"Frame: {frame}")
    meet_point_text.set_text(f"Meet: {verified_x_mp:.3f}, {verified_y_mp:.3f}, {verified_z_mp:.3f}")

    # 動作確認用にprint
    # print(f"[Frame={frame}] ConicEq: {eq_str}")
    print(f"  => MeetPoint=({verified_x_mp:.3f}, {verified_y_mp:.3f}, {verified_z_mp:.3f})")
    print(f"x_in: {x_in:.3f}, y_in: {y_in:.3f}, z_in: {z_in:.3f}")
    
    return verified_x_mp, verified_y_mp, verified_z_mp
