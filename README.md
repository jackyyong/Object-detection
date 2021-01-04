# Tensorflow对象检测 v1

1. 将Tensorflow对象检测应用于视频流; 
1. 使用网络摄像头流或视频文件; 
1. 将对象检测框的写入输出的文件。

# 如何使用:

- 必要条件: 安装了Docker的Linux
- Clone代码仓到本地
- 构建Docker脚本:
> docker build -t realtime-objectdetection .
- 配置脚本 (后续有描述)
- 执行脚本:
> bash runDocker.sh

# 配置脚本:

在exec.sh通过python函数调用中进行配置：
> python3 my-object-detection.py ...

所有可能的参数:
```
-n (--num-frames): type=int, default=0: # FPS测试需要循环的帧数

-d (--display), type=int, default=0: #是否使用窗口显示帧

-f (--fullscreen), type=int, default=0: #启用全屏显示

-o (--output), type=int, default=0: #是否应该输出修改过的视频

-on (--output-name), type=str, default="output": #输出视频文件的名字

-I (--input-device), type=int, default=0: #输入摄像头设备号

-i (--input-videos), type=str, default="": #输入视频文件路径,优先级比摄像头设备高

-w (--num-workers), type=int, default=2: #工作进程数

-q-size (--queue-size), type=int, default=5: #队列大小

-l (--logger-debug), type=int, default=0: #输出debug日志

```
#### 建议配置 (exec.sh):

- 摄像头视频流: 默认值

> python3 simple-object-detection.py -d 1 -o 1

- 视频文件流: 20工作线程, 150队列大小(调整队列以避免丢失帧)

> python3 simple-object-detection.py -d 1 -o 1 -i test.mp4 -w 20 -q-size 150

> 测试视频流：https://www.youtube.com/watch?v=DDekonb8roQ
#### 输入/输出 文件

- 输入文件在 inputs/ 目录

- 输出文件在 outputs/ 目录 (.avi)

# 工具版本:
- Ubuntu 16.04
- python 3.5
- tensorflow 1.15.2
- protobuf 3.6.1
- OpenCV 3.4.1  

# 工具安装
1. ```conda create -n p35 python=3.5 anaconda```
1. ```conda activate p35```
1. ```pip install -r requirements.txt ```

# 兼容性:
该项目旨在在Linux上运行。 不保证Windows或IOS兼容性。