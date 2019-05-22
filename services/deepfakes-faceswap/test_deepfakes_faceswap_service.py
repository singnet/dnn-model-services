import sys
import grpc

# import the generated classes
import service.service_spec.deepfakes_faceswap_pb2_grpc as grpc_bt_grpc
import service.service_spec.deepfakes_faceswap_pb2 as grpc_bt_pb2

from service import registry

VIDEO_A_TEST_URL = \
    "http://snet-models.s3.amazonaws.com/bh/Deepfakes/ben.mp4"
VIDEO_B_TEST_URL = \
    "http://snet-models.s3.amazonaws.com/bh/Deepfakes/musk.mp4"

if __name__ == "__main__":

    try:
        test_flag = False
        if len(sys.argv) == 2:
            if sys.argv[1] == "auto":
                test_flag = True

        # Service
        endpoint = input("Endpoint (localhost:{}): ".format(
            registry["deepfakes_faceswap_service"]["grpc"])) \
            if not test_flag else ""
        if endpoint == "":
            endpoint = "localhost:{}".format(
                registry["deepfakes_faceswap_service"]["grpc"])

        # Open a gRPC channel
        channel = grpc.insecure_channel("{}".format(endpoint))

        grpc_method = input("Method (faceswap): ") if not test_flag else ""
        if grpc_method == "faceswap" or grpc_method == "":
            uid = input("UID: ") if not test_flag else None
            video_a = input("Video A: ") if not test_flag else VIDEO_A_TEST_URL
            video_b = input("Video B: ") if not test_flag else VIDEO_B_TEST_URL
            model_url = input("Model URL: ") if not test_flag else None
            stub = grpc_bt_grpc.DeepFakesFaceSwapStub(channel)
            request = grpc_bt_pb2.Input(uid=uid,
                                        video_a=video_a,
                                        video_b=video_b,
                                        model_url=model_url)
            response = stub.faceswap(request)
            print(response)

            if "Fail" in str(response):
                exit(1)
        else:
            print("Invalid method!")
            exit(1)

    except Exception as e:
        print(e)
        exit(1)
