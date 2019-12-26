import sys
import grpc

# import the generated classes
import service.service_spec.video_cap_pb2_grpc as grpc_bt_grpc
import service.service_spec.video_cap_pb2 as grpc_bt_pb2

from service import registry

TEST_URL = "http://54.203.198.53:7000/Resources/v_PlayingGuitar_g03_c01.avi"

if __name__ == "__main__":

    try:
        test_flag = False
        if len(sys.argv) == 2:
            if sys.argv[1] == "auto":
                test_flag = True

        # Service VideoCaptioning
        endpoint = raw_input("Endpoint (localhost:{}): ".format(registry["video_cap_service"]["grpc"])) if not test_flag else ""
        if endpoint == "":
            endpoint = "localhost:{}".format(registry["video_cap_service"]["grpc"])

        # Open a gRPC channel
        channel = grpc.insecure_channel("{}".format(endpoint))

        grpc_method = raw_input("Method (video_cap): ") if not test_flag else ""
        if grpc_method == "video_cap" or grpc_method == "":
            url = raw_input("Url: ") if not test_flag else TEST_URL
            start_time_sec = raw_input("StartTime(s): ") if not test_flag else 0
            stop_time_sec = raw_input("StopTime (s): ") if not test_flag else 0
            stub = grpc_bt_grpc.VideoCaptioningStub(channel)
            request = grpc_bt_pb2.Input(url=url, start_time_sec=float(start_time_sec), stop_time_sec=float(stop_time_sec))
            response = stub.video_cap(request)
            print(response.value)

            if "Fail" in response.value:
                exit(1)
        else:
            print("Invalid method!")
            exit(1)

    except Exception as e:
        print(e)
        exit(1)
