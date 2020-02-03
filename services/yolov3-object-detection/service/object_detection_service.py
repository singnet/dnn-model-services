import sys
import logging

import service.common
from service.object_detection import ObjectDetector
from service import map_names

import grpc
import concurrent.futures as futures

# Importing the generated codes from buildproto.sh
import service.service_spec.object_detection_pb2_grpc as grpc_bt_grpc
from service.service_spec.object_detection_pb2 import Output

logging.basicConfig(level=10, format="%(asctime)s - [%(levelname)8s] - "
                                     "%(name)s - %(message)s")
log = logging.getLogger("obj_detect_service")


class ObjectDetectorServicer(grpc_bt_grpc.DetectServicer):
    def __init__(self):
        self.model = "yolov3"
        self.img_path = ""
        self.confidence = "0.7"

        log.debug("ObjectDetectorServicer created")

    def detect(self, request, context):
        self.img_path = request.img_path
        self.model = request.model
        self.confidence = request.confidence

        objd = ObjectDetector(self.model,
                              self.confidence,
                              map_names,
                              self.img_path)
        json_result = objd.detect()

        log.debug("detect({},{})".format(self.model, self.img_path))

        return Output(delta_time=json_result["delta_time"],
                      boxes=json_result["boxes"],
                      class_ids=json_result["class_ids"],
                      confidences=json_result["confidences"],
                      img_base64=json_result["img_base64"])


# The gRPC serve function.
#
# Params:
# max_workers: pool of threads to execute calls asynchronously
# port: gRPC server port
#
# Add all your classes to the server here.
def serve(max_workers=10, port=7777):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))
    grpc_bt_grpc.add_DetectServicer_to_server(ObjectDetectorServicer(), server)
    server.add_insecure_port("[::]:{}".format(port))
    return server


if __name__ == "__main__":
    """
    Runs the gRPC server to communicate with the Snet Daemon.
    """
    parser = service.common.common_parser(__file__)
    args = parser.parse_args(sys.argv[1:])
    service.common.main_loop(serve, args)
