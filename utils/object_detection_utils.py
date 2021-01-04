import os
from utils.app_utils import *
import numpy as np
import multiprocessing
import tensorflow as tf
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util

# 冻结检测图的路径。 这是用于对象检测的实际模型。
PATH_TO_CKPT = 'model/frozen_inference_graph.pb'

# 用于为每个框添加正确标签的字符列表。
PATH_TO_LABELS = 'model/mscoco_label_map.pbtxt'

NUM_CLASSES = 90

# 加载标签Map
label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES,
                                                            use_display_name=True)
category_index = label_map_util.create_category_index(categories)


# 检测对象
def detect_objects(image_np, session, detection_graph):
    # 由于模型期望图像具有形状，因此扩展维度：[1, None, None, 3]
    image_np_expanded = np.expand_dims(image_np, axis=0)
    image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')

    # 每个Box代表检测到的特定对象的那部分图像
    boxes = detection_graph.get_tensor_by_name('detection_boxes:0')

    # 每个分数代表每个对象的置信度。
    # 分数与分类标签一起显示在结果图像上。
    scores = detection_graph.get_tensor_by_name('detection_scores:0')
    classes = detection_graph.get_tensor_by_name('detection_classes:0')
    num_detections = detection_graph.get_tensor_by_name('num_detections:0')

    # 实际检测
    (boxes, scores, classes, num_detections) = session.run([boxes, scores, classes, num_detections],
                                                           feed_dict={image_tensor: image_np_expanded})

    # 可视化检测结果
    vis_util.visualize_boxes_and_labels_on_image_array(
        image_np,
        np.squeeze(boxes),
        np.squeeze(classes).astype(np.int32),
        np.squeeze(scores),
        category_index,
        use_normalized_coordinates=True,
        line_thickness=4)

    return image_np


# input_q 输入队列
# output_q 输出队列
def detect_worker(input_q, output_q):
    print('启动工作线程', multiprocessing.current_process().name)

    # 将一个（冻结的）Tensorflow模型加载到内存中。
    detection_graph = tf.Graph()
    with detection_graph.as_default():
        od_graph_def = tf.compat.v1.GraphDef()
        # 加载模型
        with tf.io.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
            serialized_graph = fid.read()
            od_graph_def.ParseFromString(serialized_graph)
            tf.import_graph_def(od_graph_def, name='')
        session = tf.compat.v1.Session(graph=detection_graph)

    fps = FPS().start()
    while True:
        fps.update()
        # 从输入队列中读取一项,读取后移除该项
        frame = input_q.get()

        # 检查帧对象是二维数组（视频）还是一维数组（网络摄像头）
        if len(frame) == 2:
            # output_q.put(frame[0])
            frame_rgb = cv2.cvtColor(frame[1], cv2.COLOR_BGR2RGB)
            output_q.put((frame[0], detect_objects(frame_rgb, session, detection_graph)))
        else:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            output_q.put(detect_objects(frame_rgb, session, detection_graph))
    fps.stop()
    session.close()
