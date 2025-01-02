import threading
import time
import queue

def func1(output_queue):
    """1000Hzで動作し、結果をキューに送る関数"""
    while True:
        result = time.time()  # 例として現在の時刻を返す
        print(f"func1 produced: {result}")
        output_queue.put(result)  # 結果をキューに追加
        time.sleep(0.001)  # 1000Hz (1msごと)

def func2(input_queue):
    """100Hzで動作し、func1の返り値を処理する関数"""
    while True:
        try:
            # キューからデータを取得
            data = input_queue.get(timeout=0.01)  # 10ms待機
            print(f"func2 consumed: {data}")
            # データの処理
        except queue.Empty:
            # キューが空の場合はスキップ
            continue
        time.sleep(0.01)  # 100Hz (10msごと)

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
