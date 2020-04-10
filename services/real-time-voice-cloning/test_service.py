import sys
import grpc

# import the generated classes
import service.service_spec.voice_cloning_pb2_grpc as grpc_bt_grpc
import service.service_spec.voice_cloning_pb2 as grpc_bt_pb2

from service import registry

TEST_URL = "https://raw.githubusercontent.com/singnet/dnn-model-services/master/" \
           "docs/assets/users_guide/ben_websumit19.mp3"
TEST_SNT = "Given that most of the innovation in the AI algorithm and product worlds come from students, " \
           "startups or independent developers."


if __name__ == "__main__":
    try:
        test_flag = False
        if len(sys.argv) == 2:
            if sys.argv[1] == "auto":
                test_flag = True

        endpoint = input("Endpoint (localhost:{}): ".format(
            registry["voice_cloning_service"]["grpc"])) if not test_flag else ""
        if endpoint == "":
            endpoint = "localhost:{}".format(registry["voice_cloning_service"]["grpc"])

        # open a gRPC channel
        channel = grpc.insecure_channel("{}".format(endpoint))
        audio_url = input("Audio (link): ") if not test_flag else TEST_URL
        sentence = input("Sentence (~20 words): ") if not test_flag else TEST_SNT

        stub = grpc_bt_grpc.RealTimeVoiceCloningStub(channel)
        grpc_input = grpc_bt_pb2.Input(audio_url=audio_url, sentence=sentence)

        response = stub.clone(grpc_input)
        if response.audio == b"Fail":
            print("Fail!")
            exit(1)
        print("Audio file length:", len(response.audio))
    except Exception as e:
        print(e)
        exit(1)
