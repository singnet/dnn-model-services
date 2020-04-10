import sys
import grpc

# import the generated classes
import service.service_spec.video_action_recon_pb2_grpc as grpc_bt_grpc
import service.service_spec.video_action_recon_pb2 as grpc_bt_pb2

from service import registry

TEST_URL = "http://54.203.198.53:7000/Resources/v_PlayingGuitar_g03_c01.avi"

if __name__ == "__main__":

    try:
        test_flag = False
        if len(sys.argv) == 2:
            if sys.argv[1] == "auto":
                test_flag = True

        # Service VideoCaptioning
        endpoint = input("Endpoint (localhost:{}): ".format(registry["video_action_recon_service"]["grpc"])) if not test_flag else ""
        if endpoint == "":
            endpoint = "localhost:{}".format(registry["video_action_recon_service"]["grpc"])

        # Open a gRPC channel
        channel = grpc.insecure_channel("{}".format(endpoint))

        grpc_method = input("Method (video_action_recon): ") if not test_flag else ""
        if grpc_method == "video_action_recon" or grpc_method == "":
            model = input("Model: ") if not test_flag else "400"
            url = input("Url: ") if not test_flag else TEST_URL
            stub = grpc_bt_grpc.VideoActionRecognitionStub(channel)
            request = grpc_bt_pb2.Input(model=model, url=url)
            response = stub.video_action_recon(request)
            print(response.value)

            if "Fail" in response.value:
                exit(1)
        else:
            print("Invalid method!")
            exit(1)

    except Exception as e:
        print(e)
        exit(1)
