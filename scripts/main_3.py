import time
from get import start_udp_thread, get_position

def main():
    # まずUDP受信スレッドを起動
    start_udp_thread(host='10.1.196.100', port=50006)
    
    time_step = 0
    while True:
        try:
            # (x, y, z) データを取得
            x_in, y_in, z_in = get_position(skip_rate=10, timeout=0.05)
            print(f"x_in: {x_in:.3f}, y_in: {y_in:.3f}, z_in: {z_in:.3f}")
            time_step += 1
        except StopIteration:
            print("全ての点を取得し終わりました。ループを終了します。")
            break

        # 必要に応じて極少のスリープ
        time.sleep(0.0005)

if __name__ == "__main__":
    main()
