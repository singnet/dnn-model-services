import sys
import logging
import traceback

import grpc
import concurrent.futures as futures

import service.common
from service.siggraph_colorization import Colorization

# Importing the generated codes from buildproto.sh
import service.service_spec.colorization_pb2_grpc as grpc_bt_grpc
from service.service_spec.colorization_pb2 import Output

logging.basicConfig(level=10, format="%(asctime)s - [%(levelname)8s] - %(name)s - %(message)s")
log = logging.getLogger("siggraph_colorization_service")


# Create a class to be added to the gRPC server
# derived from the protobuf codes.
class ColorizationServicer(grpc_bt_grpc.ColorizationServicer):
    def __init__(self):
        self.response = Output()
        log.debug("ColorizationServicer created")

    # The method that will be exposed to the snet-cli call command.
    # request: incoming data
    # context: object that provides RPC-specific information (timeout, etc).
    def colorize(self, request, context):
        try:
            sig_colorize = Colorization(request.img_input)
            tmp_response = sig_colorize.colorize()

            # To respond we need to fill this "img_colorized" field of Output() object (from .proto file)
            self.response.img_colorized = tmp_response["img_colorized"]

            log.debug("translate({})={}".format(request.img_input[:50], self.response.img_colorized[:50]))
            return self.response

        except Exception as e:
            traceback.print_exc()
            log.error(e)
            self.response.img_colorized = "Fail"
            return self.response


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
    grpc_bt_grpc.add_ColorizationServicer_to_server(ColorizationServicer(), server)
    server.add_insecure_port("[::]:{}".format(port))
    return server


if __name__ == "__main__":
    """
    Runs the gRPC server to communicate with the Snet Daemon.
    """
    parser = service.common.common_parser(__file__)
    args = parser.parse_args(sys.argv[1:])
    service.common.main_loop(serve, args)
