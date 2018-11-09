import grpc

# import the generated classes
import service.service_spec.ObjectDetection_ImageRecon_pb2_grpc as grpc_bt_grpc
import service.service_spec.ObjectDetection_ImageRecon_pb2 as grpc_bt_pb2

from service import registry

if __name__ == "__main__":

    try:
        endpoint = input("Endpoint (localhost:{}): ".format(registry["ObjectDetection_ImageRecon_service"]["grpc"]))
        if endpoint == "":
            endpoint = "localhost:{}".format(registry["ObjectDetection_ImageRecon_service"]["grpc"])

        # open a gRPC channel
        channel = grpc.insecure_channel("{}".format(endpoint))

        grpc_method = "detect_recon"
        model_detect = "yolov3"

        model_recon = input("Model ImageRecon (ResNet152): ")
        if model_recon == "":
            model_recon = "ResNet152"

        confidence = input("Confidence (0.7): ")
        if confidence == "":
            confidence = "0.7"

        img_path = input("Image (Link): ")

        # create a stub (client)
        stub = grpc_bt_grpc.DetectReconStub(channel)
        # create a valid request message
        request = grpc_bt_pb2.ObjDetImgReconRequest(model_detect=model_detect,
                                                    model_recon=model_recon,
                                                    confidence=confidence,
                                                    img_path=img_path)
        # make the call
        response = stub.detect_recon(request)
        print(response)

    except Exception as e:
        print(e)
