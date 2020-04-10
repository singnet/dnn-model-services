import sys
import grpc

# import the generated classes
import service.service_spec.sound_spleeter_pb2_grpc as grpc_bt_grpc
import service.service_spec.sound_spleeter_pb2 as grpc_bt_pb2

from service import registry

TEST_URL = "http://54.203.198.53:7000/Resources/audio_example.mp3"

if __name__ == "__main__":

    try:
        test_flag = False
        if len(sys.argv) == 2:
            if sys.argv[1] == "auto":
                test_flag = True

        endpoint = input("Endpoint (localhost:{}): ".format(
            registry["sound_spleeter_service"]["grpc"])) if not test_flag else ""
        if endpoint == "":
            endpoint = "localhost:{}".format(registry["sound_spleeter_service"]["grpc"])

        # Open a gRPC channel
        channel = grpc.insecure_channel("{}".format(endpoint))
        url = input("Audio (URL): ") if not test_flag else TEST_URL
        stub = grpc_bt_grpc.SoundSpleeterStub(channel)
        request = grpc_bt_pb2.Input(audio_url=url)
        response = stub.spleeter(request)
        if b"Fail" in [response.vocals, response.accomp]:
            print("Fail!")
            exit(1)
        print(len(response.vocals), len(response.accomp))

    except Exception as e:
        print(e)
        exit(1)
