import sys
import logging

from aiohttp import web
from jsonrpcserver.aio import methods

import services.common

logging.basicConfig(
    level=10, format="%(asctime)s - [%(levelname)8s] - %(name)s - %(message)s")
log = logging.getLogger('basic_service_two')

'''
Add a new method like this:

@methods.add
asynf def my_new_method(**kwargs):

    # if kwargs = {"algorithm": "my_algo","image": "ousd8fua0sduf..."}
    algorithm = kwargs.get("algorithm", None)
    image = kwargs.get("image", None)

    # Now you can work with both parameters
    # At the end, returns the result as a JSON:

    return {'result_1': 'Nice aldo!', 'result_2': 'Good image!' ...}
'''


@methods.add
async def echo(**kwargs):
    log.debug(f'echo({kwargs})')
    return {'result': f'Echo: {kwargs}'}


@methods.add
async def version(**kwargs):
    log.debug('version()')
    return {'result': 'v0.1'}


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
