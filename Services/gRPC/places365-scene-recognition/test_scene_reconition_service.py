import grpc
import service.service_spec.scene_recognition_pb2_grpc as grpc_bt_grpc
import service.service_spec.scene_recognition_pb2 as grpc_bt_pb2
from service import registry
from service.serviceUtils import base64_to_jpg

if __name__ == "__main__":

    # Open a gRPC channel to endpoint given by registry
    channel = grpc.insecure_channel("localhost:{}".format(registry["scene_recognition_service"]["grpc"]))
    print("Opened channel")

    # Fill request
    grpc_method = "recognize_scene"
    input_image = \
        "https://cdn.the961.com/wp-content/uploads/2017/06/beach-in-lebanon-1.png"
    predict = "IO, Attributes"

    try:
        # Create a stub (client)
        stub = grpc_bt_grpc.SceneRecognitionStub(channel)
        # Create a valid request message
        request = grpc_bt_pb2.SceneRecognitionRequest(input_image=input_image,
                                                      predict=predict)
        # Make the call
        response = stub.recognize_scene(request)

        # Treat response
        print("Result: {}".format(response.data))
        #base64_to_jpg(response.data, "/Shared/scene_recognition_test_output.jpg")
        print("Service completed!")

    except Exception as e:
        print(e)
