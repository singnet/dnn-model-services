import sys
import logging
import datetime
import hashlib

import multiprocessing

import grpc
import concurrent.futures as futures

from . import common
from .video_action_recon import VideoActionRecognizer

# Importing the generated codes from buildproto.sh
import service.service_spec.video_action_recon_pb2_grpc as grpc_bt_grpc
from service.service_spec.video_action_recon_pb2 import Output

logging.basicConfig(level=10, format="%(asctime)s - [%(levelname)8s] - %(name)s - %(message)s")
log = logging.getLogger("video_action_recon_service")


def mp_video_action_recon(obj, return_dict):
    return_dict["response"] = obj.video_action_recon()


# Create a class to be added to the gRPC server
# derived from the protobuf codes.
class VideoActionRecognitionServicer(grpc_bt_grpc.VideoActionRecognitionServicer):
    def __init__(self):
        self.uid = ""
        self.model = "600"
        self.url = ""
        # Just for debugging purpose.
        log.debug("VideoActionRecognitionServicer created")

    # The method that will be exposed to the snet-cli call command.
    # request: incoming data
    # context: object that provides RPC-specific information (timeout, etc).
    def video_action_recon(self, request, _):
        self.uid = generate_uid()
        self.model = request.model
        self.url = request.url

        obj = VideoActionRecognizer(self.uid, self.model, self.url)

        manager = multiprocessing.Manager()
        return_dict = manager.dict()

        p = multiprocessing.Process(target=mp_video_action_recon, args=(obj, return_dict))
        p.start()
        p.join()

        response = return_dict.get("response", None)
        if not response:
            return Output(value="Fail")

        log.debug("video_action_recon({},{})=OK".format(self.model, self.url))
        return Output(value=response["Top5Actions"])


def generate_uid():
    # Setting a hash accordingly to the timestamp
    seed = "{}".format(datetime.datetime.now())
    m = hashlib.sha256()
    m.update(seed.encode("utf-8"))
    m = m.hexdigest()
    # Returns only the first and the last 10 hex
    return m[:10] + m[-10:]


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
