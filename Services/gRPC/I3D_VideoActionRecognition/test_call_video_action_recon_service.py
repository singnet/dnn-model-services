import grpc

# import the generated classes
import service.service_spec.video_action_recon_pb2_grpc as grpc_bt_grpc
import service.service_spec.video_action_recon_pb2 as grpc_bt_pb2

from service import registry

if __name__ == "__main__":

    try:
        # Service VideoCaptioning
        endpoint = input("Endpoint (localhost:{}): ".format(registry["video_action_recon_service"]["grpc"]))
        if endpoint == "":
            endpoint = "localhost:{}".format(registry["video_action_recon_service"]["grpc"])

        # Open a gRPC channel
        channel = grpc.insecure_channel("{}".format(endpoint))

        grpc_method = input("Method (video_action_recon): ")
        if grpc_method == "video_action_recon" or grpc_method == "":
            url = input("Url: ")
            model = input("Model: ")
            # Create a stub (client)
            stub = grpc_bt_grpc.VideoActionRecognitionStub(channel)
            # Create a valid request message
            request = grpc_bt_pb2.Input(model=model, url=url)
            # Make the call
            response = stub.video_action_recon(request)
            print(response.value)
        else:
            print("Invalid method!")

    except Exception as e:
        print(e)
