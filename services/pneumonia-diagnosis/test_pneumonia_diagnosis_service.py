import sys
import grpc

# import the generated classes
import service.service_spec.pneumonia_diagnosis_pb2_grpc as grpc_bt_grpc
import service.service_spec.pneumonia_diagnosis_pb2 as grpc_bt_pb2

from service import registry

TEST_URL = "https://snet-models.s3.amazonaws.com/bh/PneumoniaDiagnosis/diagnosis_pneumonia.jpg"

if __name__ == "__main__":

    try:
        test_flag = False
        if len(sys.argv) == 2:
            if sys.argv[1] == "auto":
                test_flag = True

        endpoint = input("Endpoint (localhost:{}): ".format(
            registry["pneumonia_diagnosis_service"]["grpc"])) \
            if not test_flag else ""

        if endpoint == "":
            endpoint = "localhost:{}".format(
                registry["pneumonia_diagnosis_service"]["grpc"])

        # open a gRPC channel
        channel = grpc.insecure_channel("{}".format(endpoint))

        grpc_method = input("Method (check): ") if not test_flag else "check"
        img_path = input("Image (Link): ") if not test_flag else TEST_URL

        stub = grpc_bt_grpc.DiagnosisStub(channel)
        grpc_input = grpc_bt_pb2.Input(img_path=img_path)

        if grpc_method == "check":
            response = stub.check(grpc_input)
            print(response.output)
        else:
            print("Invalid method!")
            exit(1)

    except Exception as e:
        print(e)
        exit(1)
