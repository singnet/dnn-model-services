import sys
import logging

from aiohttp import web
from jsonrpcserver.aio import methods
from jsonrpcserver.exceptions import InvalidParams

import services.common

logging.basicConfig(
    level=10, format="%(asctime)s - [%(levelname)8s] - %(name)s - %(message)s")
log = logging.getLogger('basic_service_one')


'''
Simple arithmetic service to test the Snet Daemon, dApp and/or Snet-CLI.
The user must provide the method (arithmetic operation) and
two numeric inputs: "a" and "b".

e.g:
With dApp:  'method': add
            'params': {"a": "12", "b": "5"}
Resulting:  'result': {"result": "17"}


Full JSON:
{
    "jsonrpc": "2.0",
    "method": "add",
    "params": {"a": "12", "b": "5"},
    "id": 1
}

Result:
{
    "jsonrpc": "2.0",
    "result": {"result": "17"},
    "id": 1
}

'''


@methods.add
async def add(**kwargs):
    a = kwargs.get("a", None)
    b = kwargs.get("b", None)

    log.debug(f"add({a},{b})")

    if a is None:
        raise InvalidParams('"a" is required')

    if b is None:
        raise InvalidParams('"b" is required')

    if type(a) is str:
        if a.isdigit():
            a = int(a)
        else:
            raise InvalidParams('"a" must be a number')

    if type(b) is str:
        if b.isdigit():
            b = int(b)
        else:
            raise InvalidParams('"b" must be a number')

    result = a + b
    return {'result': result}


@methods.add
async def sub(**kwargs):
    a = kwargs.get("a", None)
    b = kwargs.get("b", None)

    log.debug(f"sub({a},{b})")

    if a is None:
        raise InvalidParams('"a" is required')

    if b is None:
        raise InvalidParams('"b" is required')

    if type(a) is str:
        if a.isdigit():
            a = int(a)
        else:
            raise InvalidParams('"a" must be a number')

    if type(b) is str:
        if b.isdigit():
            b = int(b)
        else:
            raise InvalidParams('"b" must be a number')

    result = a - b
    return {'result': result}


@methods.add
async def mul(**kwargs):
    a = kwargs.get("a", None)
    b = kwargs.get("b", None)

    log.debug(f"mul({a},{b})")

    if a is None:
        raise InvalidParams('"a" is required')

    if b is None:
        raise InvalidParams('"b" is required')

    if type(a) is str:
        if a.isdigit():
            a = int(a)
        else:
            raise InvalidParams('"a" must be a number')

    if type(b) is str:
        if b.isdigit():
            b = int(b)
        else:
            raise InvalidParams('"b" must be a number')

    result = a * b
    return {'result': result}


@methods.add
async def div(**kwargs):
    a = kwargs.get("a", None)
    b = kwargs.get("b", None)

    log.debug(f"div({a},{b})")

    if a is None:
        raise InvalidParams('"a" is required')

    if b is None:
        raise InvalidParams('"b" is required')

    if type(a) is str:
        if a.isdigit():
            a = int(a)
        else:
            raise InvalidParams('"a" must be a number')

    if type(b) is str:
        if b.isdigit():
            b = int(b)
        else:
            raise InvalidParams('"b" must be a number')

    result = a / b
    return {'result': result}


async def json_rpc_handle(request):
    request = await request.text()
    response = await methods.dispatch(request, trim_log_values=True)
    if response.is_notification:
        return web.Response()
    else:
        return web.json_response(response, status=response.http_status)


if __name__ == '__main__':
    '''
    Runs the JSON-RPC server to communicate with the Snet Daemon.
    '''
    parser = services.common.common_parser(__file__)
    args = parser.parse_args(sys.argv[1:])
    services.common.main_loop(json_rpc_handle, args)
