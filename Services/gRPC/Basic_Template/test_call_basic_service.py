import grpc

# import the generated classes
import service.model.basic_tamplate_rpc_pb2_grpc as grpc_bt_grpc
import service.model.basic_tamplate_rpc_pb2 as grpc_bt_pb2

from service import registry

if __name__ == '__main__':

    try:
        # Service ONE - Arithmetics
        endpoint = input('Endpoint (localhost:{}): '.format(
            registry['basic_service_one']['grpc']))
        if endpoint == '':
            endpoint = 'localhost:{}'.format(
                registry['basic_service_one']['grpc'])

        # Open a gRPC channel
        channel = grpc.insecure_channel('{}'.format(
            endpoint))

        grpc_method = input('Method (add|sub|mul|div): ')
        a = float(input('Number 1: '))
        b = float(input('Number 2: '))

        if grpc_method == 'add':
            # create a stub (client)
            stub = grpc_bt_grpc.AdditionStub(channel)
            # create a valid request message
            number = grpc_bt_pb2.Numbers(a=a, b=b)
            # make the call
            response = stub.add(number)
            print(response.value)

        elif grpc_method == 'sub':
            # create a stub (client)
            stub = grpc_bt_grpc.SubtractionStub(channel)
            # create a valid request message
            number = grpc_bt_pb2.Numbers(a=a, b=b)
            # make the call
            response = stub.sub(number)
            print(response.value)

        elif grpc_method == 'mul':
            # create a stub (client)
            stub = grpc_bt_grpc.MultiplicationStub(channel)
            # create a valid request message
            number = grpc_bt_pb2.Numbers(a=a, b=b)
            # make the call
            response = stub.mul(number)
            print(response.value)

        elif grpc_method == 'div':
            # create a stub (client)
            stub = grpc_bt_grpc.DivisionStub(channel)
            # create a valid request message
            number = grpc_bt_pb2.Numbers(a=a, b=b)
            # make the call
            response = stub.div(number)
            # et voilà
            print(response.value)

        else:
            print('Invalid method!')

    except Exception as e:
        print(e)
