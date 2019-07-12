import sys
import logging

import grpc
import concurrent.futures as futures

import service.common
from service.pneumonia_diagnosis import diagnosis

# Importing the generated codes from buildproto.sh
import service.service_spec.pneumonia_diagnosis_pb2_grpc as grpc_bt_grpc
from service.service_spec.pneumonia_diagnosis_pb2 import Output

logging.basicConfig(level=10, format="%(asctime)s - [%(levelname)8s] - "
                                     "%(name)s - %(message)s")
log = logging.getLogger("pneumonia_diagnosis_service")


# Create a class to be added to the gRPC server
# derived from the protobuf codes.
class DiagnosisServicer(grpc_bt_grpc.DiagnosisServicer):
    def __init__(self):
        # Just for debugging purpose.
        log.debug("DiagnosisServicer created")

    # The method that will be exposed to the snet-cli call command.
    # request: incoming data
    # context: object that provides RPC-specific information (timeout, etc).
    def check(self, request, context):
        # To respond we need to create a Output() object (from .proto file)
        response = Output(output=diagnosis(request.img_path))
        log.debug("check({})={}".format(request.img_path[:50],
                                        response.output))
        return response


# The gRPC serve function.
#
# Params:
# max_workers: pool of threads to execute calls asynchronously
# port: gRPC server port
#
# Add all your classes to the server here.
def serve(max_workers=10, port=7777):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))
    grpc_bt_grpc.add_DiagnosisServicer_to_server(DiagnosisServicer(), server)
    server.add_insecure_port("[::]:{}".format(port))
    return server


if __name__ == "__main__":
    """
    Runs the gRPC server to communicate with the Snet Daemon.
    """
    parser = service.common.common_parser(__file__)
    args = parser.parse_args(sys.argv[1:])
    service.common.main_loop(serve, args)
