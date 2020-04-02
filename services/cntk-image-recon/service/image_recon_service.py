import sys
import logging

import multiprocessing

import grpc
import concurrent.futures as futures

import service.common
from service import flowers_map_names, dogs_map_names

# Importing the generated codes from buildproto.sh
import service.service_spec.image_recon_pb2_grpc as grpc_bt_grpc
from service.service_spec.image_recon_pb2 import Output

logging.basicConfig(level=10, format="%(asctime)s - [%(levelname)8s] - %(name)s - %(message)s")
log = logging.getLogger("image_recon_service")


def mp_image_recognition(method, request, map_names, image_dims, return_dict):
    import service.image_recon as img_recon
    return_dict["response"] = img_recon.image_recognition(method,
                                                          request.model,
                                                          map_names,
                                                          request.img_path,
                                                          image_dims)


# Create a class to be added to the gRPC server
# derived from the protobuf codes.
class RecognizerServicer(grpc_bt_grpc.RecognizerServicer):
    def __init__(self):
        self.model = "ResNet152"
        self.img_path = ""
        # Just for debugging purpose.
        log.debug("RecognizerServicer created")

    # The method that will be exposed to the snet-cli call command.
    # request: incoming data
    # context: object that provides RPC-specific information (timeout, etc).
    def flowers(self, request, _):
        manager = multiprocessing.Manager()
        return_dict = manager.dict()
        p = multiprocessing.Process(target=mp_image_recognition, args=("flowers",
                                                                       request,
                                                                       flowers_map_names,
                                                                       (3, 224, 224),
                                                                       return_dict))
        p.start()
        p.join()

        response = return_dict.get("response", None)
        if not response:
            return Output(delta_time="Fail", top_5="Fail")

        log.debug("flowers({},{})=OK".format(self.model, self.img_path))
        return Output(delta_time=response["delta_time"], top_5=str(response["top_5"]))

    def dogs(self, request, _):
        manager = multiprocessing.Manager()
        return_dict = manager.dict()
        p = multiprocessing.Process(target=mp_image_recognition, args=("dogs",
                                                                       request,
                                                                       dogs_map_names,
                                                                       (3, 224, 224),
                                                                       return_dict))
        p.start()
        p.join()

        response = return_dict.get("response", None)
        if not response:
            return Output(delta_time="Fail", top_5="Fail")

        log.debug("flowers({},{})=OK".format(self.model, self.img_path))
        return Output(delta_time=response["delta_time"], top_5=str(response["top_5"]))


# The gRPC serve function.
#
# Params:
# max_workers: pool of threads to execute calls asynchronously
# port: gRPC server port
#
# Add all your classes to the server here.
def serve(max_workers=10, port=7777):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))
    grpc_bt_grpc.add_RecognizerServicer_to_server(RecognizerServicer(), server)
    server.add_insecure_port("[::]:{}".format(port))
    return server


if __name__ == "__main__":
    """
    Runs the gRPC server to communicate with the Snet Daemon.
    """
    parser = service.common.common_parser(__file__)
    args = parser.parse_args(sys.argv[1:])
    service.common.main_loop(serve, args)
