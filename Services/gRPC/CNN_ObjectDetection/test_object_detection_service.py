import grpc

# import the generated classes
import service.service_spec.object_detection_pb2_grpc as grpc_bt_grpc
import service.service_spec.object_detection_pb2 as grpc_bt_pb2

from service import registry

if __name__ == "__main__":

    try:
        endpoint = input(
            "Endpoint (localhost:{}): ".format(registry["object_detection_service"]["grpc"])
        )
        if endpoint == "":
            endpoint = "localhost:{}".format(registry["object_detection_service"]["grpc"])

        # open a gRPC channel
        channel = grpc.insecure_channel("{}".format(endpoint))

        grpc_method = "detect"
        model = "yolov3"
        confidence = input("Confidence (0.7): ")
        if confidence == "":
            confidence = "0.7"

        img_path = input("Image (Path or Link): ")

        # create a stub (client)
        stub = grpc_bt_grpc.DetectStub(channel)
        # create a valid request message
        request = grpc_bt_pb2.ObjectDetectionRequest(model=model,
                                                     confidence=confidence,
                                                     img_path=img_path)
        # make the call
        response = stub.detect(request)
        print(response)

    except Exception as e:
        print(e)
