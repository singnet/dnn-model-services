import jsonrpcclient
from services import registry

if __name__ == '__main__':

    try:
        opt = input('Which service (1|2)? ')
        if opt == '1':
            # Service ONE - Arithmetics
            jsonrpc_method = input('Which method (add|sub|mul|div)? ')
            a = input('Number 1: ')
            b = input('Number 2: ')
            jsonrpc_port = registry['basic_service_one']['jsonrpc']
            jsonrpcclient.request(f"http://127.0.0.1:{jsonrpc_port}",
                                  jsonrpc_method,
                                  a=a,
                                  b=b)
        elif opt == '2':
            # Service TWO - Basic Echo
            jsonrpc_method = input('Which method (version|echo)? ')
            jsonrpc_port = registry['basic_service_two']['jsonrpc']
            jsonrpcclient.request(f"http://127.0.0.1:{jsonrpc_port}",
                                  jsonrpc_method,
                                  test="testing...")
        else:
            print('Service unavailable!')

    except Exception as e:
        print(e)
