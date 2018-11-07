import sys
import logging

import grpc
import concurrent.futures as futures

from . import common
from .video_action_recon import VideoActionRecognizer

# Importing the generated codes from buildproto.sh
import service.service_spec.video_action_recon_pb2_grpc as grpc_bt_grpc
from service.service_spec.video_action_recon_pb2 import Result

logging.basicConfig(level=10, format="%(asctime)s - [%(levelname)8s] - %(name)s - %(message)s")
log = logging.getLogger("video_action_recon_service")


# Create a class to be added to the gRPC server
# derived from the protobuf codes.
class VideoActionRecognitionServicer(grpc_bt_grpc.VideoActionRecognitionServicer):
    def __init__(self):
        self.model = "600"
        self.url = ""
        self.result = "Fail"
        # Just for debugging purpose.
        log.debug("VideoActionRecognitionServicer created")

    # The method that will be exposed to the snet-cli call command.
    # request: incoming data
    # context: object that provides RPC-specific information (timeout, etc).
    def video_action_recon(self, request, context):
        self.model = request.model
        self.url = request.url

        # To respond we need to create a Result() object (from .proto file)
        self.result = Result()

        video_recon_instance = VideoActionRecognizer(self.model, self.url)
        self.result.value = str(video_recon_instance.video_action_recon())

        log.debug("video_action_recon({},{})={}".format(self.model, self.url, self.result.value))

        return self.result


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
    grpc_bt_grpc.add_VideoActionRecognitionServicer_to_server(VideoActionRecognitionServicer(), server)
    server.add_insecure_port("[::]:{}".format(port))
    return server


if __name__ == "__main__":
    """
    Runs the gRPC server to communicate with the SNET Daemon.
    """
    parser = common.common_parser(__file__)
    args = parser.parse_args(sys.argv[1:])
    common.main_loop(serve, args)
