import sys
import logging

import grpc
import concurrent.futures as futures

import service.common
import service.image_recon as img_recon
from service import flowers_map_names, dogs_map_names, cars_map_names

# Importing the generated codes from buildproto.sh
import service.service_spec.image_recon_pb2_grpc as grpc_bt_grpc
from service.service_spec.image_recon_pb2 import Result

logging.basicConfig(level=10, format="%(asctime)s - [%(levelname)8s] - %(name)s - %(message)s")
log = logging.getLogger("image_recon_service")


# Create a class to be added to the gRPC server
# derived from the protobuf codes.
class FlowersServicer(grpc_bt_grpc.FlowersServicer):
    def __init__(self):
        self.model = "ResNet152"
        self.img_path = ""
        self.result = "Fail"

        # Just for debugging purpose.
        log.debug("FlowersServicer created")

    # The method that will be exposed to the snet-cli call command.
    # request: incoming data
    # context: object that provides RPC-specific information (timeout, etc).
    def flowers(self, request, context):
        # In our case, request is a Numbers() object (from .proto file)
        self.img_path = request.img_path
        self.model = request.model

        map_names = flowers_map_names
        image_dims = (3, 224, 224)
        json_result = img_recon.image_recognition("flowers", self.model, map_names, self.img_path, image_dims)

        # To respond we need to create a Result() object (from .proto file)
        self.result = Result()
        self.result.top_5 = str(json_result["top_5"]).encode("utf-8")
        self.result.delta_time = str(json_result["delta_time"]).encode("utf-8")
        log.debug("flowers({},{})={}".format(self.model, self.img_path, self.result.top_5))
        return self.result


class DogsServicer(grpc_bt_grpc.DogsServicer):
    def __init__(self):
        self.model = "ResNet152"
        self.img_path = ""
        self.result = "Fail"
        log.debug("DogsServicer created")

    def dogs(self, request, context):

        self.img_path = request.img_path
        self.model = request.model

        map_names = dogs_map_names
        image_dims = (3, 224, 224)
        json_result = img_recon.image_recognition("dogs", self.model, map_names, self.img_path, image_dims)

        self.result = Result()
        self.result.top_5 = str(json_result["top_5"]).encode("utf-8")
        self.result.delta_time = str(json_result["delta_time"]).encode("utf-8")
        log.debug("dogs({},{})={}".format(self.model, self.img_path, self.result.top_5))
        return self.result


class CarsServicer(grpc_bt_grpc.CarsServicer):
    def __init__(self):
        self.model = "ResNet152"
        self.img_path = ""
        self.result = "Fail"
        log.debug("CarsServicer created")

    def cars(self, request, context):

        self.img_path = request.img_path
        self.model = request.model

        map_names = cars_map_names
        image_dims = (3, 224, 224)
        json_result = img_recon.image_recognition("cars", self.model, map_names, self.img_path, image_dims)

        self.result = Result()
        self.result.top_5 = str(json_result["top_5"]).encode("utf-8")
        self.result.delta_time = str(json_result["delta_time"]).encode("utf-8")
        log.debug("cars({},{})={}".format(self.model, self.img_path, self.result.top_5))
        return self.result


# The gRPC serve function.
#
# Params:
# max_workers: pool of threads to execute calls asynchronously
# port: gRPC server port
#
# Add all your classes to the server here.
def serve(max_workers=10, port=7777):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))
    grpc_bt_grpc.add_FlowersServicer_to_server(FlowersServicer(), server)
    grpc_bt_grpc.add_DogsServicer_to_server(DogsServicer(), server)
    grpc_bt_grpc.add_CarsServicer_to_server(CarsServicer(), server)
    server.add_insecure_port("[::]:{}".format(port))
    return server


if __name__ == "__main__":
    """
    Runs the gRPC server to communicate with the Snet Daemon.
    """
    parser = service.common.common_parser(__file__)
    args = parser.parse_args(sys.argv[1:])
    service.common.main_loop(serve, args)
