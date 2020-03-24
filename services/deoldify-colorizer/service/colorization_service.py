import sys
import logging
import traceback

import grpc
import concurrent.futures as futures

from torch.multiprocessing import Manager, Process, set_start_method
try:
     set_start_method('spawn')
except RuntimeError:
    pass

import service.common
from service.colorization import Colorization

# Importing the generated codes from buildproto.sh
import service.service_spec.colorization_pb2_grpc as grpc_bt_grpc
from service.service_spec.colorization_pb2 import Output

logging.basicConfig(level=10, format="%(asctime)s - [%(levelname)8s] - %(name)s - %(message)s")
log = logging.getLogger("colorization_service")


def mp_colorize(obj, return_dict):
    return_dict["response"] = obj.colorize()


# Create a class to be added to the gRPC server
# derived from the protobuf codes.
class ColorizationServicer(grpc_bt_grpc.ColorizationServicer):
    def __init__(self):
        log.debug("ColorizationServicer created")

    # The method that will be exposed to the snet-cli call command.
    # request: incoming data
    # context: object that provides RPC-specific information (timeout, etc).
    def colorize(self, request, _):
        try:
            obj = Colorization(request.img_input, request.render_factor)

            manager = Manager()
            return_dict = manager.dict()
            p = Process(target=mp_colorize, args=(obj, return_dict))
            p.start()
            p.join()

            response = return_dict.get("response", None)
            if not response:
                return Output()

            log.debug("colorize({})={}".format(request.img_input[:50], response["img_colorized"][:50]))
            return Output(img_colorized=response["img_colorized"])

        except Exception as e:
            traceback.print_exc()
            log.error(e)
            return Output()


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
