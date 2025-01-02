import socket
import struct
import threading
import queue
import time

# グローバル変数
DATA_QUEUE = queue.Queue(maxsize=1000)  # UDP受信データを格納するキュー

def udp_receiver(host, port):
    """
    UDPで受信したデータをDATA_QUEUEに格納するスレッド関数。
    受信データは6つのdouble(x1, y1, z1, x2, y2, z2)であると想定。
    """
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 2**20)  # バッファサイズを増加
    udp_socket.bind((host, port))
    print(f"[get.py] UDPクライアントを起動しました: {host}:{port}")

    while True:
        data, _ = udp_socket.recvfrom(1024)  # データ受信(最大1024バイト)
        try:
            decoded_data = struct.unpack('6d', data)  # 6つのdoubleをデコード
            DATA_QUEUE.put(decoded_data, timeout=0.1) # キューに追加
        except queue.Full:
            pass
            # print("[get.py] データキューが満杯です。データを破棄します。")
        except struct.error:
            print("[get.py] デコードエラーが発生しました。")

def start_udp_thread(host='10.216.71.90', port=50006):
    """
    UDP受信スレッドを起動する関数。
    メインコードで呼び出すことで、バックグラウンドで受信を開始する。
    """
    receiver_thread = threading.Thread(
        target=udp_receiver, 
        args=(host, port),
        daemon=True
    )
    receiver_thread.start()

def get_position(skip_rate=10, timeout=0.05):
    """
    1. skip_rate個分のデータを破棄し、最後の1件のみを (x1,y1,z1) として返す。
    2. キューが空の場合は短いタイムアウト（timeout秒）だけ待ち、
       その間にデータが届かなければ StopIteration を起こす。
    
    これにより、古いデータで溜まることなく最新データを取得しつつ、
    サーバが停止して本当にデータが来なくなったら終了できる。
    """

    last_data = None
    for i in range(skip_rate):
        try:
            # キューから1件取り出し（timeout秒以内に来なければqueue.Empty）
            last_data = DATA_QUEUE.get(timeout=timeout)
        except queue.Empty:
            # まだデータが来ない(=サーバが送っていない)場合は、
            # i==0 (最初の取り出しも失敗) のときだけ StopIteration にする
            # -> 途中なら skip_rate の全部揃わなくても最新データを返す
            if i == 0 and last_data is None:
                raise StopIteration
            # これまでに取り出せていたデータがあるならループを抜ける
            break

    if last_data is None:
        # キューが空のまま or データが1度も取得できなかった
        raise StopIteration

    x1, y1, z1, x2, y2, z2 = last_data
    x1 = x1 + 1.000
    y1 = y1 - 0.666
    z1 = z1 - 2.140
    return x1, y1, z1
