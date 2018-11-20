import sys
import grpc

# import the generated classes
import service.service_spec.video_action_recon_pb2_grpc as grpc_bt_grpc
import service.service_spec.video_action_recon_pb2 as grpc_bt_pb2

from service import registry

TEST_URL = "http://crcv.ucf.edu/THUMOS14/UCF101/UCF101/v_CricketShot_g04_c02.avi"

if __name__ == "__main__":

    try:
        test_flag = False
        if len(sys.argv) == 2:
            if sys.argv[1] == "test":
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
            # Create a stub (client)
            stub = grpc_bt_grpc.VideoActionRecognitionStub(channel)
            # Create a valid request message
            request = grpc_bt_pb2.Input(model=model, url=url)
            # Make the call
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
