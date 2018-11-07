import grpc

# import the generated classes
import service.service_spec.video_cap_pb2_grpc as grpc_bt_grpc
import service.service_spec.video_cap_pb2 as grpc_bt_pb2

from service import registry

if __name__ == "__main__":

    try:
        # Service VideoCaptioning
        endpoint = raw_input("Endpoint (localhost:{}): ".format(registry["video_cap_service"]["grpc"]))
        if endpoint == "":
            endpoint = "localhost:{}".format(registry["video_cap_service"]["grpc"])

        # Open a gRPC channel
        channel = grpc.insecure_channel("{}".format(endpoint))

        grpc_method = raw_input("Method (video_cap): ")
        if grpc_method == "video_cap" or grpc_method == "":
            url = raw_input("Url: ")
            start_time_sec = raw_input("StartTime(s): ")
            stop_time_sec = raw_input("StopTime (s): ")
            # Create a stub (client)
            stub = grpc_bt_grpc.VideoCaptioningStub(channel)
            # Create a valid request message
            request = grpc_bt_pb2.Input(url=url, start_time_sec=start_time_sec, stop_time_sec=stop_time_sec)
            # Make the call
            response = stub.video_cap(request)
            print(response.value)
        else:
            print("Invalid method!")

    except Exception as e:
        print(e)
