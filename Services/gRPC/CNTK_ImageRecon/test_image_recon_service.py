import grpc

# import the generated classes
import service.service_spec.image_recon_pb2_grpc as grpc_bt_grpc
import service.service_spec.image_recon_pb2 as grpc_bt_pb2

from service import registry

if __name__ == "__main__":

    try:
        endpoint = input("Endpoint (localhost:{}): ".format(registry["image_recon_service"]["grpc"]))
        if endpoint == "":
            endpoint = "localhost:{}".format(registry["image_recon_service"]["grpc"])

        # open a gRPC channel
        channel = grpc.insecure_channel("{}".format(endpoint))

        grpc_method = input("Method (flowers|dogs): ")

        model = input("Model (ResNet152): ")
        if model == "":
            model = "ResNet152"

        img_path = input("Image (Link): ")

        if grpc_method == "flowers":
            # create a stub (client)
            stub = grpc_bt_grpc.FlowersStub(channel)
            # create a valid request message
            number = grpc_bt_pb2.ImageReconRequest(model=model, img_path=img_path)
            # make the call
            response = stub.flowers(number)
            # et voilà
            print(response.delta_time)
            print(response.top_5)

        elif grpc_method == "dogs":
            # create a stub (client)
            stub = grpc_bt_grpc.DogsStub(channel)
            # create a valid request message
            number = grpc_bt_pb2.ImageReconRequest(model=model, img_path=img_path)
            # make the call
            response = stub.dogs(number)
            # et voilà
            print(response.delta_time)
            print(response.top_5)

        elif grpc_method == "cars":
            # create a stub (client)
            stub = grpc_bt_grpc.CarsStub(channel)
            # create a valid request message
            number = grpc_bt_pb2.ImageReconRequest(model=model, img_path=img_path)
            # make the call
            response = stub.cars(number)
            # et voilà
            print(response.delta_time)
            print(response.top_5)

        else:
            print("Invalid method!")

    except Exception as e:
        print(e)
