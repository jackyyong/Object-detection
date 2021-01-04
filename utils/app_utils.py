from threading import Thread
import datetime
import cv2

class FPS:
    def __init__(self):
        # 存储开始时间,结束时间,以及总帧数
        self._start = None
        self._end = None
        self._numFrames = 0

    def start(self):
        # 启动计时器
        self._start = datetime.datetime.now()
        return self
    
    def stop(self):
        # 展厅计时器
        self._end = datetime.datetime.now()

    def update(self):
        # 增加开始和结束间隔期间检查的帧总数
        self._numFrames += 1

    def elapsed(self):
        # 返回开始和结束间隔之间的总秒数
        return (self._end - self._start).total_seconds()

    def fps(self):
        # 计算每秒（大约）帧数
        return self._numFrames / self.elapsed()

    
class WebcamVideoStream:
    def __init__(self, src=0):
        # 初始化摄像机流并从流中读取第一帧
        self.stream = cv2.VideoCapture(src)
        (self.grabbed, self.frame) = self.stream.read()
        
        # 初始化用于线程暂停标志
        self.stopped = False

    def start(self):
        # 启动线程以从视频流中读取帧
        Thread(target=self.update, args=()).start()
        return self
 
    def update(self):
        # 无限循环，直到线程停止
        while True:
            # 如果设置了线程暂停标志，停止线程
            if self.stopped:
                return
                    
            # 否则，从视频流中读取下一帧
            (self.grabbed, self.frame) = self.stream.read()
 
    def read(self):
        # 返回最近读取的帧
        return self.grabbed, self.frame
 
    def stop(self):
        # 设置线程暂停标志
        self.stopped = True

    def getWidth(self):
        # 获得帧宽度
        return int(self.stream.get(cv2.CAP_PROP_FRAME_WIDTH))

    def getHeight(self):
        # 获得帧高度
        return int(self.stream.get(cv2.CAP_PROP_FRAME_HEIGHT))

    def getFPS(self):
        # 获得帧率
        return int(self.stream.get(cv2.CAP_PROP_FPS))

    def isOpen(self):
        # 获得帧是否已经打开标志
        return self.stream.isOpened()

    def setFramePosition(self, framePos):
        self.stream.set(cv2.CAP_PROP_POS_FRAMES, framePos)

    def getFramePosition(self):
        return int(self.stream.get(cv2.CAP_PROP_POS_FRAMES))

    def getFrameCount(self):
        return int(self.stream.get(cv2.CAP_PROP_FRAME_COUNT))
