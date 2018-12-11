import grpc

# import the generated classes
import service.service_spec.scene_recognition_pb2_grpc as grpc_bt_grpc
import service.service_spec.scene_recognition_pb2 as grpc_bt_pb2
from service import registry

if __name__ == "__main__":

    # open a gRPC channel
    endpoint = "localhost:{}".format(registry["super_resolution_service"]["grpc"])
    channel = grpc.insecure_channel("{}".format(endpoint))
    print("opened channel")

    # fill request
    grpc_method = "recognize_scene"
    input_image = \
        "https://www.gettyimages.ie/gi-resources/images/Homepage/Hero/UK/CMS_Creative_164657191_Kingfisher.jpg"
    predict = "scene"

    try:
        if grpc_method == "recognize_scene":
            # create a stub (client)
            stub = grpc_bt_grpc.SceneRecognitionStub(channel)
            # create a valid request message
            request = grpc_bt_pb2.SceneRecognitionRequest(input_image=input_image,
                                                         predict=predict)
            # make the call
            response = stub.recognize_scene(request)

            # et voilà
            base64_to_jpg(response.data, "/Shared/scene_recognition_test_output.jpg")
            print("Service completed!")
        else:
            print("Invalid method!")

    except Exception as e:
        print(e)
