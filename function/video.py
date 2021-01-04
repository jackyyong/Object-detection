from __future__ import print_function
from utils.app_utils import *
from utils.object_detection_utils import *
import argparse
import multiprocessing
from multiprocessing import Queue, Pool
from queue import PriorityQueue
import cv2

def video(args):
    """
    从视频文件流读取并应用对象检测
    """

    # 如果需要，将multiprocessing日志级别设置为debug
    if args["logger_debug"]:
        logger = multiprocessing.log_to_stderr()
        logger.setLevel(multiprocessing.SUBDEBUG)

    print(" --> queue_size=", args["queue_size"])
    print(" --> num_workers=", args["num_workers"])

    # 多处理：初始化输入输出队列，输出优先级队列和工作进程池
    input_q = Queue(maxsize=args["queue_size"])
    output_q = Queue(maxsize=args["queue_size"])
    output_pq = PriorityQueue(maxsize=3 * args["queue_size"])

    # 每个工作进程在它启动时将会调用initializer(*initargs)
    pool = Pool(processes=args["num_workers"],
                initializer=detect_worker,
                initargs=(input_q, output_q))

    # 创建了一个线程化视频流, 并启动FPS计数器
    # 从视频文件，图像序列或摄像机捕获视频
    videoCapture = cv2.VideoCapture("inputs/{}".format(args["input_videos"]))
    fps = FPS().start()

    # 定义输出编解码器并创建VideoWriter对象
    if args["output"]:
        fourcc = cv2.VideoWriter_fourcc(*'MP4V')
        out = cv2.VideoWriter('outputs/{}.mp4'.format(args["output_name"]),
                              fourcc, videoCapture.get(cv2.CAP_PROP_FPS),
                              (int(videoCapture.get(cv2.CAP_PROP_FRAME_WIDTH)),
                               int(videoCapture.get(cv2.CAP_PROP_FRAME_HEIGHT))))

    # 开始读取和处理视频流
    if args["display"] > 0:
        print()
        print("=====================================================================")
        print("开始视频采集。 按\"q\"（在视频窗口上）退出。")
        print("=====================================================================")
        print()

    # 读取帧计数器
    countReadFrame = 0
    # 写入帧计数器
    countWriteFrame = 1
    # 视频总帧数
    nFrame = int(videoCapture.get(cv2.CAP_PROP_FRAME_COUNT))

    # 读取了第一帧标志位
    firstReadFrame = True
    # 处理了第一帧标志位
    firstTreatedFrame = True
    # 已使用第一帧标志位
    firstUsedFrame = True
    while True:
        # 检查输入队列是否满了
        if not input_q.full():
            # 读取帧, 并存储在输入队列中
            ret, frame = videoCapture.read()
            if ret:
                input_q.put((int(videoCapture.get(cv2.CAP_PROP_POS_FRAMES)), frame))
                countReadFrame = countReadFrame + 1
                print(" --> 读取第", countReadFrame, "帧完成")
                if firstReadFrame:
                    print(" --> 从视频文件读取第一帧,传递给输入队列。\n")
                    firstReadFrame = False

        # 检查输出队列不是空的
        if not output_q.empty():
            # 恢复输出队列中的已处理帧，进入优先队列
            output_pq.put(output_q.get())
            if firstTreatedFrame:
                print(" --> 恢复第一个已处理的帧.\n")
                firstTreatedFrame = False

        # 检查优先队列是不是空的
        if not output_pq.empty():
            prior, output_frame = output_pq.get()
            if prior > countWriteFrame:
                output_pq.put((prior, output_frame))
            else:
                countWriteFrame = countWriteFrame + 1
                output_rgb = cv2.cvtColor(output_frame, cv2.COLOR_RGB2BGR)

                # 将帧写入文件
                if args["output"]:
                    out.write(output_rgb)

                # 显示结果帧
                if args["display"]:
                    cv2.imshow('Video Object Detection', output_rgb)
                    fps.update()

                if firstUsedFrame:
                    print(" --> 开始使用恢复的帧（显示 和/或 写入）。\n")
                    firstUsedFrame = False

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        print(
            "读取帧: %-3i %% -- 写入帧: %-3i %%" % (int(countReadFrame / nFrame * 100), int(countWriteFrame / nFrame * 100)),
            end='\r')
        if ((not ret) & input_q.empty() & output_q.empty() & output_pq.empty()):
            break

    print("\n文件已被成功读取并处理:\n  --> {}/{} 读取帧 \n  --> {}/{} 写入帧 \n".format(countReadFrame, nFrame, countWriteFrame - 1,
                                                                        nFrame))

    # 结束后,释放capture
    fps.stop()
    pool.terminate()
    print(" --> 终止线程池处理。\n")
    videoCapture.release()
    if args["output"]:
        out.release()
    cv2.destroyAllWindows()
