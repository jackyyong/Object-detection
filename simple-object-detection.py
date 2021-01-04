from __future__ import print_function
from function.realtime import *
from function.video import *
import argparse
import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

if __name__ == '__main__':

    # 构建参数解析并解析参数
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", "--num-frames", type=int, default=0, help="# of frames to loop over for FPS test")
    ap.add_argument("-d", "--display", type=int, default=0, help="Whether or not frames should be displayed")
    ap.add_argument("-o", "--output", type=int, default=0, help="Whether or not modified videos shall be writen")
    ap.add_argument("-on", "--output-name", type=str, default="output", help="Name of the output video file")
    ap.add_argument("-I", "--input-device", type=int, default=0, help="Device number input")
    ap.add_argument("-i", "--input-videos", type=str, default="", help="Path to videos input, overwrite device input if used")
    ap.add_argument('-w', '--num-workers', dest='num_workers', type=int, default=2, help='Number of workers.')
    ap.add_argument('-q-size', '--queue-size', dest='queue_size', type=int, default=5, help='Size of the queue.')
    ap.add_argument('-l', '--logger-debug', dest='logger_debug', type=int, default=0, help='Print logger debug')
    ap.add_argument('-f', '--fullscreen', dest='full_screen', type=int, default=0, help='enable full screen')
    args = vars(ap.parse_args())

    # 如果没有视频文件输入,则使用摄像头视频流
    if args['input_videos'] == "":
        realtime(args)
    # 否则,使用视频文件流
    else:
        video(args)
