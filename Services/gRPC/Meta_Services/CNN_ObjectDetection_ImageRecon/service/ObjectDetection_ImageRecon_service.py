import sys
import logging

import service.common
from service.ObjectDetection_ImageRecon_service import DetectRecon
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
        self.model_objDet = "yolov3"
        self.model_imgRecon = "ResNet152"
        self.img_path = ""
        self.result = "Fail"
        self.confidence = "0.7"
        log.debug("DetectReconServicer created")

    def detect_recon(self, request, context):
        self.img_path = request.img_path
        self.model = request.model
        self.confidence = request.confidence

        # Instanciate an object of the Service.
        obj_service = DetectRecon(map_names, self.img_path)

        # Setting ObjectDetection Service params
        name = "objDetect"
        agent_addr = "0x1E89D9ed5bCC22F934AF631CdA771019081E57B2"
        method = "detect"
        json_txt = '{"model": "yolov3", "img_path": "https://www.thetraveltart.com/wp-content/uploads/2010/12/Las-Vegas-Traffic.jpg", "confidence": "0.9"}'
        obj_service.snet_set_params(name, agent_addr, method, json_txt)

        # Setting Imagerecon Service params
        name = "imgRecon"
        agent_addr = "0x9211Ca9A96063401BaAC5cafE85efC4024325279"
        method = "dogs"
        json_txt = '{"model": "ResNet152", "img_path": "https://d17fnq9dkz9hgj.cloudfront.net/uploads/2018/03/Pomeranian_01-390x203.jpeg"}'
        obj_service.snet_set_params(name, agent_addr, method, json_txt)

        json_result = obj_service.detect_recon()

        self.result = Result()
        self.result.delta_time = str(json_result["delta_time"]).encode("utf-8")
        self.result.boxes = str(json_result["boxes"]).encode("utf-8")
        self.result.confidences = str(json_result["confidences"]).encode("utf-8")
        self.result.img_base64 = str(json_result["img_base64"]).encode("utf-8")
        log.debug("detect({},{})={}".format(self.model, self.img_path, self.result))
        return self.result

        return {"result": obj_service.detect()}


# The gRPC serve function.
#
# Params:
# max_workers: pool of threads to execute calls asynchronously
# port: gRPC server port
#
# Add all your classes to the server here.
def serve(max_workers=10, port=7777):
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
    service.common.main_loop(serve, args)
