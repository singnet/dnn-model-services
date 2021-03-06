import sys
import logging

import grpc
import concurrent.futures as futures

import service.common

# Importing the generated codes from buildproto.sh
import service.service_spec.sound_spleeter_pb2_grpc as grpc_bt_grpc
from service.service_spec.sound_spleeter_pb2 import Output

import service.sound_spleeter as ss

# TensorFlow.
import tensorflow as tf
# Using session to consume less GPU memory
tf_session_config = tf.ConfigProto()
tf_session_config.gpu_options.allow_growth = True
sess = tf.Session(config=tf_session_config)

from spleeter.separator import Separator
separator = Separator("spleeter:2stems")
separator._get_predictor()  # Hacky!


logging.basicConfig(level=10, format="%(asctime)s - [%(levelname)8s] - %(name)s - %(message)s")
log = logging.getLogger("sound_spleeter_service")


# Create a class to be added to the gRPC server
# derived from the protobuf codes.
class SoundSpleeterServicer(grpc_bt_grpc.SoundSpleeterServicer):
    def __init__(self):
        # Just for debugging purpose.
        log.debug("SoundSpleeterServicer created")

    @staticmethod
    def spleeter(request, context):
        response = ss.spleeter(separator, request.audio_url, request.audio)
        if not response or "error" in response:
            error_msg = response.get("error", "") if response else ""
            log.error(error_msg)
            context.set_details(error_msg)
            context.set_code(grpc.StatusCode.INTERNAL)
            return Output()

        log.debug("clone({},{})={},{}".format(request.audio_url[:10],
                                              len(request.audio),
                                              len(response["vocals"]),
                                              len(response["accomp"])))
        return Output(vocals=response["vocals"], accomp=response["accomp"])


# The gRPC serve function.
#
# Params:
# max_workers: pool of threads to execute calls asynchronously
# port: gRPC server port
#
# Add all your classes to the server here.
# (from generated .py files by protobuf compiler)
def serve(max_workers=4, port=7777):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers), options=[
        ('grpc.max_send_message_length', 25 * 1024 * 1024),
        ('grpc.max_receive_message_length', 25 * 1024 * 1024)])
    grpc_bt_grpc.add_SoundSpleeterServicer_to_server(SoundSpleeterServicer(), server)
    server.add_insecure_port("[::]:{}".format(port))
    return server


if __name__ == "__main__":
    """
    Runs the gRPC server to communicate with the SNET Daemon.
    """
    parser = service.common.common_parser(__file__)
    args = parser.parse_args(sys.argv[1:])
    service.common.main_loop(serve, args)
