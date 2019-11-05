import sys
import logging
import traceback
import time

import grpc
import concurrent.futures as futures
from threading import Thread

from content_server import ContentServer

from . import common
from .deepfakes_faceswap import FaceSwapper

# Importing the generated codes from buildproto.sh
import service.service_spec.deepfakes_faceswap_pb2_grpc as grpc_bt_grpc
from service.service_spec.deepfakes_faceswap_pb2 import Output

logging.basicConfig(level=10, format="%(asctime)s - [%(levelname)8s] "
                                     "- %(name)s - %(message)s")
log = logging.getLogger("deepfakes_faceswap_service")

# Content Server
cs = None
admin_pwd = "admin#deepfakes"
cs_host = "0.0.0.0"
cs_port = 7062


# Create a class to be added to the gRPC server
# derived from the protobuf codes.
class DeepFakesFaceSwapServicer(grpc_bt_grpc.DeepFakesFaceSwapServicer):
    def __init__(self):
        self.uid = ""
        self.response = "Fail"
        
        # Just for debugging purpose.
        log.debug("DeepFakesFaceSwapServicer created")

    # The method that will be exposed to the snet-cli call command.
    # request: incoming data
    # context: object that provides RPC-specific information (timeout, etc).
    def faceswap(self, request, context):
        self.response = Output()
        try:
            self.response.uid, _ = cs.add(uid=request.uid,
                                          service_name="deepfakes_faceswap",
                                          rpc_method="faceswap_model",
                                          message="Received",
                                          content_type="url",
                                          func=self.process_request,
                                          args={"request": request})
            self.response.uid, _ = cs.add(uid=self.response.uid,
                                          service_name="deepfakes_faceswap",
                                          rpc_method="faceswap_video",
                                          message="Received",
                                          content_type="url",
                                          func=self.process_request,
                                          args={"request": request})

            self.response.uid = "http://52.38.111.172:7062/" \
                                "dashboard?uid={}".format(self.response.uid)

            return self.response

        except Exception as e:
            traceback.print_exc()
            log.error(e)
            self.response.uid = "Fail"
            return self.response

    @staticmethod
    def process_request(uid, content_id, rpc_method, **kwargs):
        # Waiting for queue
        queue_pos = cs.queue_get_pos(content_id)
        while queue_pos != 0:
            queue_pos = cs.queue_get_pos(content_id)
            time.sleep(1)
    
        request = None
        for k, v in kwargs.items():
            if k == "request":
                request = v

        if request:
            if rpc_method == "faceswap_model":
                fs = FaceSwapper(uid,
                                 request.model_url,
                                 request.video_a,
                                 request.video_b)

                content = fs.faceswap(cs, content_id, model=True)

                if "error" in content:
                    cs.update(content_id,
                              message=content["error"],
                              queue_pos=-2,
                              content=content["error"])
                else:
                    # Got the response, update DB with expiration and content
                    cs.update(content_id,
                              queue_pos=-1,
                              message="Done",
                              expiration="1d",
                              content=content["model"])

                log.info("{}({})={} [Ready]".format(rpc_method,
                                                    content_id,
                                                    content))
            elif rpc_method == "faceswap_video":
                fs = FaceSwapper(uid,
                                 request.model_url,
                                 request.video_a,
                                 request.video_b)

                content = fs.faceswap(cs, content_id)

                if "error" in content:
                    cs.update(content_id,
                              message=content["error"],
                              queue_pos=-2,
                              content=content["error"])
                else:
                    # Got the response, update DB with expiration and content
                    cs.update(content_id,
                              queue_pos=-1,
                              message="Done",
                              expiration="1d",
                              content=content["video"])

                log.info("{}({})={} [Ready]".format(rpc_method,
                                                    content_id,
                                                    content))
            else:
                log.error("Invalid RPC Method!")
        else:
            log.error("Invalid Request!")


# The gRPC serve function.
#
# Params:
# max_workers: pool of threads to execute calls asynchronously
# port: gRPC server port
#
# Add all your classes to the server here.
# (from generated .py files by protobuf compiler)
def serve(max_workers=10, port=7777):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))
    grpc_bt_grpc.add_DeepFakesFaceSwapServicer_to_server(
        DeepFakesFaceSwapServicer(), server)
    server.add_insecure_port("[::]:{}".format(port))
    return server


def init_content_server():
    global cs
    cs = ContentServer(host=cs_host,
                       port=cs_port,
                       admin_pwd=admin_pwd,
                       log=log)
    
    log.info("Creating Content Server Database...")
    cs.create()
    
    # Start Content Server at 0.0.0.0:7062 with "admin" as the admin password
    log.info("Starting Content Server...")
    cs.serve()


if __name__ == "__main__":
    """
    Runs the gRPC server to communicate with the SNET Daemon.
    """
    parser = common.common_parser(__file__)
    args = parser.parse_args(sys.argv[1:])
    
    # Initiate Content Server (Database and Server)
    content_server_th = Thread(target=init_content_server, daemon=True)
    content_server_th.start()
    
    common.main_loop(serve, args)
