import sys
import logging

import service.common
from service.ObjectDetection_ImageRecon import DetectRecon
from service import map_names

import grpc
import concurrent.futures as futures

# Importing the generated codes from buildproto.sh
import service.model.ObjectDetection_ImageRecon_pb2_grpc as grpc_bt_grpc
from service.model.ObjectDetection_ImageRecon_pb2 import Result

logging.basicConfig(
    level=10, format="%(asctime)s - [%(levelname)8s] - %(name)s - %(message)s"
)
log = logging.getLogger("ObjectDetection_ImageRecon_service")


class DetectReconServicer(grpc_bt_grpc.DetectReconServicer):
    """
    Class of the service, with the method detect_recon() used by gRPC.
    """

    def __init__(self):
        self.flag_start_th = False
        self.model_detect = "yolov3"
        self.model_recon = "ResNet152"
        self.img_path = ""
        self.result = "Fail"
        self.confidence = "0.7"
        log.debug("DetectReconServicer created")

    def detect_recon(self, request, context):
        self.img_path = request.img_path
        self.model_detect = request.model_detect
        self.model_recon = request.model_recon
        self.confidence = request.confidence

        # Instanciate an object of the Service.
        obj_service = DetectRecon(self.model_detect, self.model_recon, self.img_path)

        # Setting ObjectDetection Service params
        name = "objDetect"
        agent_addr = "0x1E89D9ed5bCC22F934AF631CdA771019081E57B2"
        method = "detect"
        json_txt = '{"model": "%s", "img_path": "%s", "confidence": "%s"}' % (
            self.model_detect,
            self.img_path,
            self.confidence,
        )
        obj_service.snet_set_params(name, agent_addr, method, json_txt)
        json_result = obj_service.detect_recon()

        self.result = Result()
        self.result.delta_time = str(json_result["delta_time"]).encode("utf-8")
        self.result.boxes = str(json_result["boxes"]).encode("utf-8")
        self.result.confidences = str(json_result["confidences"]).encode("utf-8")
        self.result.class_ids = str(json_result["class_ids"]).encode("utf-8")
        self.result.top_1_list = str(json_result["top_1_list"]).encode("utf-8")

        log.debug(
            "detect_recon({},{},{},{})={}".format(
                self.model_detect,
                self.model_recon,
                self.confidence,
                self.img_path,
                str(self.result)[:500],
            )
        )
        return self.result


# The gRPC serve function.
#
# Params:
# max_workers: pool of threads to execute calls asynchronously
# port: gRPC server port
#
# Add all your classes to the server here.
def grpc_server(max_workers=10, port=7777):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))
    grpc_bt_grpc.add_DetectReconServicer_to_server(DetectReconServicer(), server)
    server.add_insecure_port("[::]:{}".format(port))
    return server


if __name__ == "__main__":
    """
    Runs the gRPC server to communicate with the Snet Daemon.
    """
    parser = service.common.common_parser(__file__)
    args = parser.parse_args(sys.argv[1:])
    service.common.main_loop(grpc_server, args)
