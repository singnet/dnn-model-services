import sys
import grpc

# import the generated classes
import service.service_spec.colorization_pb2_grpc as grpc_bt_grpc
import service.service_spec.colorization_pb2 as grpc_bt_pb2

from service import registry

TEST_URL = "https://snet-models.s3.amazonaws.com/bh/Colorize/jucelino.jpg"

if __name__ == "__main__":

    try:
        test_flag = False
        if len(sys.argv) == 2:
            if sys.argv[1] == "auto":
                test_flag = True

        endpoint = input("Endpoint (localhost:{}): ".format(registry["siggraph_colorization_service"]["grpc"])) if not test_flag else ""
        if endpoint == "":
            endpoint = "localhost:{}".format(registry["siggraph_colorization_service"]["grpc"])

        # open a gRPC channel
        channel = grpc.insecure_channel("{}".format(endpoint))

        grpc_method = input("Method (colorize): ") if not test_flag else "colorize"
        if grpc_method == "":
            grpc_method = "colorize"

        img_input = input("Image (Link): ") if not test_flag else TEST_URL

        stub = grpc_bt_grpc.ColorizationStub(channel)
        grpc_input = grpc_bt_pb2.Input(img_input=img_input)

        if grpc_method == "colorize":
            response = stub.colorize(grpc_input)
            print(response.img_colorized)

            if response.img_colorized == "Fail":
                exit(1)
        else:
            print("Invalid method!")
            exit(1)

    except Exception as e:
        print(e)
        exit(1)
