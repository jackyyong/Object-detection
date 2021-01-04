from __future__ import print_function
from utils.app_utils import *
from utils.object_detection_utils import *
import argparse
import multiprocessing
from multiprocessing import Queue, Pool
import cv2

def realtime(args):
    """
    读取并在输入的实时摄像头视频流上应用对象检测
    """

    # 如果在没有定义帧数限制的情况下关闭了显示：将显示设置为开
    if((not args["display"]) & (args["num_frames"] < 0)):
        print("\nSet display to on\n")
        args["display"] = 1

    # 如果需要，将multiprocessing日志级别设置为debug
    if args["logger_debug"]:
        logger = multiprocessing.log_to_stderr()
        logger.setLevel(multiprocessing.SUBDEBUG)

    # multiprocessing：初始化输入和输出队列和工作池
    input_q = Queue(maxsize=args["queue_size"])
    output_q = Queue(maxsize=args["queue_size"])
    pool = Pool(processes=args["num_workers"],
                initializer=detect_worker,
                initargs=(input_q, output_q))

    # 创建一个线程化视频流并启动了FPS计数器
    vs = WebcamVideoStream(src=args["input_device"]).start()
    fps = FPS().start()

    # 定义输出编解码器并创建VideoWriter对象
    if args["output"]:
        fourcc = cv2.VideoWriter_fourcc(*'MP4V')
        out = cv2.VideoWriter('outputs/{}.mp4'.format(args["output_name"]), fourcc, vs.getFPS()/args["num_workers"], (vs.getWidth(), vs.getHeight()))

    # 开始读取和处理视频流
    if args["display"] > 0:
        print()
        print("=====================================================================")
        print("开始视频采集。 按\"q\"（在视频窗口上）退出。")
        print("=====================================================================")
        print()

    countFrame = 0
    while True:
        # 逐帧捕获
        ret, frame = vs.read()
        countFrame = countFrame + 1
        if ret:
            input_q.put(frame)
            output_rgb = cv2.cvtColor(output_q.get(), cv2.COLOR_RGB2BGR)

            # 写入帧
            if args["output"]:
                out.write(output_rgb)

            # 显示结果帧
            if args["display"]:
                ## 全屏显示
                if args["full_screen"]:
                    cv2.namedWindow("Webcam Object Detection", cv2.WND_PROP_FULLSCREEN)
                    cv2.setWindowProperty("Webcam Object Detection",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
                cv2.imshow("Webcam Object Detection", output_rgb)
                fps.update()
            elif countFrame >= args["num_frames"]:
                break

        else:
            break

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # 结束后,释放capture
    fps.stop()
    pool.terminate()
    vs.stop()
    if args["output"]:
        out.release()
    cv2.destroyAllWindows()

