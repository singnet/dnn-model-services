import sys
import logging
import datetime
import hashlib

import grpc
import concurrent.futures as futures

import multiprocessing

from . import common

# Importing the generated codes from buildproto.sh
from service_spec import video_cap_pb2_grpc as grpc_bt_grpc
from service_spec.video_cap_pb2 import Output

logging.basicConfig(level=10, format="%(asctime)s - [%(levelname)8s] - %(name)s - %(message)s")
log = logging.getLogger("video_cap")


def mp_captions(url, uid, start_time_sec, stop_time_sec, return_dict):
    from video_captioner import VideoCaptioner
    vc = VideoCaptioner(url, uid, start_time_sec, stop_time_sec, 0, 0)
    return_dict["response"] = vc.get_video_captions()


# Create a class to be added to the gRPC server
# derived from the protobuf codes.
class VideoCaptioningServicer(grpc_bt_grpc.VideoCaptioningServicer):
    def __init__(self):
        self.url = ""
        self.start_time_sec = 0
        self.stop_time_sec = 0
        self.uid = ""

        # Just for debugging purpose.
        log.debug("VideoCaptioningServicer created")

    # The method that will be exposed to the snet-cli call command.
    # request: incoming data
    # context: object that provides RPC-specific information (timeout, etc).
    def video_cap(self, request, _):
        self.url = request.url
        self.start_time_sec = request.start_time_sec
        self.stop_time_sec = request.stop_time_sec
        self.uid = generate_uid()

        manager = multiprocessing.Manager()
        return_dict = manager.dict()
        worker = multiprocessing.Process(
            target=mp_captions,
            args=(self.url, self.uid, self.start_time_sec, self.stop_time_sec, return_dict))
        worker.start()
        worker.join()

        response = return_dict.get("response", None)
        if not response:
            return Output(value="Fail")
        
        log.debug("video_cap({},{},{})={}".format(self.url,
                                                  self.start_time_sec,
                                                  self.stop_time_sec,
                                                  response["Caption"]))
        return Output(value=response["Caption"])


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
