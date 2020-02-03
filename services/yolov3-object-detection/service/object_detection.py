import numpy as np
import os
import time
import requests
import base64
import cv2
import traceback
import datetime
import hashlib
import logging

from service.service_spec.object_detection_pb2 import Boxes

logging.basicConfig(level=10, format="%(asctime)s - [%(levelname)8s] - %(name)s - %(message)s")
log = logging.getLogger("object_detection_service")

resources_root = os.path.join("..", "..", "utils", "Resources")


class ObjectDetector:
    def __init__(self, model, confidence, map_names, img_path):
        self.model = model
        self.confidence = confidence
        self.map_names = map_names
        self.img_path = img_path
        self.colors = []
        self.classes = []

    @staticmethod
    # Get the names of the output layers
    def get_output_layers(net):
        layer_names = net.getLayerNames()
        output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
        return output_layers

    # Draw the predicted bounding box
    def draw_pred(self, img, class_id, conf, left, top, right, bottom):
        label = "%.2f" % conf
        if self.map_names:
            assert class_id < len(self.map_names)
            label = "%s:%s" % (self.map_names[class_id], label)
        cv2.rectangle(img, (left, top), (right, bottom), self.colors[class_id], 2)
        cv2.rectangle(img, (left, top), (right, top + 15), self.colors[class_id], cv2.FILLED)
        cv2.putText(img, label, (left, top + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(255, 255, 255))

    def detect(self):
        tmp_img_file = generate_uid() + ".jpg"
        try:
            start_time = time.time()
            # Link
            if "http://" in self.img_path or "https://" in self.img_path:
                header = {'User-Agent': 'Mozilla/5.0 (Windows NT x.y; Win64; x64; rv:9.0) Gecko/20100101 Firefox/10.0'}
                r = requests.get(self.img_path, headers=header, allow_redirects=True)
                with open(tmp_img_file, "wb") as my_f:
                    my_f.write(r.content)
                    self.img_path = tmp_img_file

            # Base64
            elif len(self.img_path) > 500:
                img_data = base64.b64decode(self.img_path)
                with open(tmp_img_file, "wb") as f:
                    f.write(img_data)
                    self.img_path = tmp_img_file

            if self.model.upper() == "YOLOV3":
                model_file = os.path.join(resources_root, "Models", "yolov3.weights")
                model_config = os.path.join(resources_root, "Models", "yolov3.cfg")

                self.classes = [v for k, v in self.map_names.items()]
                self.colors = np.random.uniform(0, 255, size=(len(self.classes), 3))

                net = cv2.dnn.readNet(model_file, model_config)

                image = cv2.imread(self.img_path)
                w_image = image.shape[1]
                h_image = image.shape[0]
                scale = 0.00392

                blob = cv2.dnn.blobFromImage(image, scale, (416, 416), (0, 0, 0), True, crop=False)
                net.setInput(blob)
                outs = net.forward(self.get_output_layers(net))

                class_ids = []
                confidences = []
                boxes = []
                conf_threshold = 0.4
                nms_threshold = 0.4

                for out in outs:
                    for detection in out:
                        scores = detection[5:]
                        class_id = np.argmax(scores)
                        confidence = scores[class_id]
                        if confidence >= float(self.confidence):
                            center_x = int(detection[0] * w_image)
                            center_y = int(detection[1] * h_image)
                            w = int(detection[2] * w_image)
                            h = int(detection[3] * h_image)
                            x = center_x - w / 2
                            y = center_y - h / 2
                            class_ids.append(class_id)
                            confidences.append(float(confidence))
                            boxes.append([x, y, w, h])

                indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)

                ret_boxes = []
                ret_class_ids = []
                ret_confidences = []

                for i in indices:
                    i = i[0]
                    box = boxes[i]
                    x = box[0]
                    y = box[1]
                    w = box[2]
                    h = box[3]
                    self.draw_pred(
                        image,
                        class_ids[i],
                        confidences[i],
                        round(x),
                        round(y),
                        round(x + w),
                        round(y + h),
                    )
                    ret_boxes.append(Boxes(x=round(x), y=round(y), w=w, h=h))
                    ret_class_ids.append(class_ids[i])
                    ret_confidences.append(confidences[i])

                _, buffer = cv2.imencode(".jpg", image)
                img_base64 = base64.b64encode(buffer)

                delta_time = time.time() - start_time

                if os.path.exists(tmp_img_file):
                    os.remove(tmp_img_file)

                return {
                    "delta_time": delta_time,
                    "boxes": ret_boxes,
                    "class_ids": ret_class_ids,
                    "confidences": ret_confidences,
                    "img_base64": img_base64.decode("utf-8"),
                }

            else:
                if os.path.exists(tmp_img_file):
                    os.remove(tmp_img_file)
                return {
                    "delta_time": 0,
                    "boxes": [],
                    "class_ids": [],
                    "confidences": [],
                    "img_base64": b"Fail",
                }

        except Exception as e:
            log.error(e)
            traceback.print_exc()
            if os.path.exists(tmp_img_file):
                os.remove(tmp_img_file)
            return {
                "delta_time": 0,
                "boxes": [],
                "class_ids": [],
                "confidences": [],
                "img_base64": b"Fail",
            }


def generate_uid():
    # Setting a hash accordingly to the timestamp
    seed = "{}".format(datetime.datetime.now())
    m = hashlib.sha256()
    m.update(seed.encode("utf-8"))
    m = m.hexdigest()
    # Returns only the first and the last 10 hex
    return m[:10] + m[-10:]
