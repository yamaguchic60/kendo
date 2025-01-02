import socket
import struct
import threading
import queue

# グローバル変数
DATA_QUEUE = queue.Queue(maxsize=1000)  # データキュー（最大1000個）

def udp_receiver(host, port):
    """
    UDPデータを受信し、キューに格納するスレッド関数。
    """
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 2**20)  # バッファサイズを増加
    udp_socket.bind((host, port))
    print(f"UDPクライアントを起動しました: {host}:{port}")

    while True:
        data, _ = udp_socket.recvfrom(1024)  # データ受信
        try:
            decoded_data = struct.unpack('6d', data)  # デコード
            DATA_QUEUE.put(decoded_data, timeout=0.1)  # キューに追加
        except queue.Full:
            print("データキューが満杯です。データを破棄します。")
        except struct.error:
            print("デコードエラーが発生しました。")


def display_coordinates(skip_rate=10):
    """
    受信データをコンソールに表示し、指定したスキップ率でリアルタイム性を保つ関数。

    Parameters:
        skip_rate (int): データを表示する頻度（例: 10の場合、10個に1個を表示）。
    """
    counter = 0  # スキップカウンタ

    while True:
        if not DATA_QUEUE.empty():
            data = DATA_QUEUE.get()  # キューからデータ取得
            counter += 1

            # skip_rateの割合で表示
            if counter % skip_rate == 0:
                x1, y1, z1, x2, y2, z2 = data
                print(f"受信座標: Point1({x1:.3f}, {y1:.3f}, {z1:.3f}) Point2({x2:.3f}, {y2:.3f}, {z2:.3f})")
                counter = 0  # カウンタをリセット


if __name__ == "__main__":
    HOST = '10.1.196.100'
    PORT = 50006

    # UDP受信スレッドを起動
    receiver_thread = threading.Thread(target=udp_receiver, args=(HOST, PORT), daemon=True)
    receiver_thread.start()

    # データを表示（10個に1個のデータを表示）
    display_coordinates(skip_rate=10)
