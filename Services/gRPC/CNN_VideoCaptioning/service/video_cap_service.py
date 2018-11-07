import sys
import logging

import grpc
import concurrent.futures as futures

from . import common
from video_captioner import VideoCaptioner

# Importing the generated codes from buildproto.sh
from service_spec import video_cap_pb2_grpc as grpc_bt_grpc
from service_spec.video_cap_pb2 import Result

logging.basicConfig(level=10, format="%(asctime)s - [%(levelname)8s] - %(name)s - %(message)s")
log = logging.getLogger("video_cap")


# Create a class to be added to the gRPC server
# derived from the protobuf codes.
class VideoCaptioningServicer(grpc_bt_grpc.VideoCaptioningServicer):
    def __init__(self):
        self.url = ''
        self.start_time_sec = 0
        self.stop_time_sec = 0
        self.result = 'Fail'
        # Just for debugging purpose.
        log.debug("VideoCaptioningServicer created")

    # The method that will be exposed to the snet-cli call command.
    # request: incoming data
    # context: object that provides RPC-specific information (timeout, etc).
    def video_cap(self, request, context):
        self.url = request.url
        self.start_time_sec = int(request.start_time_sec)
        self.stop_time_sec = int(request.stop_time_sec)

        # To respond we need to create a Result() object (from .proto file)
        self.result = Result()

        video_cap_instance = VideoCaptioner(self.url, 'tmp_video', self.start_time_sec, self.stop_time_sec, 0, 0)
        self.result.value = str(video_cap_instance.get_captions())

        log.debug("video_cap({},{},{})={}".format(self.url, self.start_time_sec, self.stop_time_sec, self.result.value))

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
    grpc_bt_grpc.add_VideoCaptioningServicer_to_server(VideoCaptioningServicer(), server)
    server.add_insecure_port("[::]:{}".format(port))
    return server


if __name__ == "__main__":
    """
    Runs the gRPC server to communicate with the SNET Daemon.
    """
    parser = common.common_parser(__file__)
    args = parser.parse_args(sys.argv[1:])
    common.main_loop(serve, args)
