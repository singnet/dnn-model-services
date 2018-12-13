import sys
import grpc

import service.service_spec.scene_recognition_pb2_grpc as grpc_bt_grpc
import service.service_spec.scene_recognition_pb2 as grpc_bt_pb2

from service import registry
from service.serviceUtils import base64_to_jpg

TEST_URL = "https://cdn.the961.com/wp-content/uploads/2017/06/beach-in-lebanon-1.png"

if __name__ == "__main__":

    try:
        test_flag = False
        if len(sys.argv) == 2:
            if sys.argv[1] == "auto":
                test_flag = True

        # If running a test script, fill request automatically
        if test_flag:
            # Open a gRPC channel to endpoint given by registry
            endpoint = "localhost:{}".format(registry["scene_recognition_service"]["grpc"])
            # Fill request
            grpc_method = "recognize_scene"
            input_image = TEST_URL
            predict = "IO, Attributes"
        else:
            endpoint = raw_input("Endpoint (localhost:{})".format(registry["scene_recognition_service"]["grpc"]))
            grpc_method = "recognize_scene"
            input_image = raw_input("Image URL: ")
            predict = raw_input("Pick what to predict (csv: io, attributes, categories, cam): ")

        if grpc_method == "recognize_scene":
            # Open a channel to grpc endpoint
            channel = grpc.insecure_channel(endpoint)
            print("Opened channel")
            # Create a stub (client)
            stub = grpc_bt_grpc.SceneRecognitionStub(channel)
            # Create a valid request message
            request = grpc_bt_pb2.SceneRecognitionRequest(input_image=input_image,
                                                          predict=predict)
            # Make the call
            response = stub.recognize_scene(request)

            # Print and treat response
            response_dict = response.data
            print("TEST RESULT: ")
            for key in response_dict:
                if key == "cam":
                    base64_to_jpg(response_dict["cam"], "./test_cam.jpg")
                    print("CAM saved to ./test_cam.jpg")
                else:
                    print("{}: {}".format(key, response_dict[key]))
            print("Service completed!")
        else:
            print("Invalid method!")
            exit(1)

    except Exception as e:
        print(e)
        exit(1)
