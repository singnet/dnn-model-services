import sys
import logging

from aiohttp import web
from jsonrpcserver.aio import methods
from jsonrpcserver.exceptions import InvalidParams

import service.common
import service.image_recon as img_recon
from service import flowers_map_names, dogs_map_names

logging.basicConfig(
    level=10, format="%(asctime)s - [%(levelname)8s] - %(name)s - %(message)s"
)
log = logging.getLogger("img_recon_service")


@methods.add
async def version(**kwargs):
    log.debug("version()")
    return {"result": "v0.1"}


@methods.add
async def flowers(**kwargs):
    log.debug("flowers({})".format(kwargs))
    model = kwargs.get("model", "ResNet18")
    map_names = flowers_map_names
    img_path = kwargs.get("img_path", None)
    if img_path is None:
        raise InvalidParams('"img_path" is required')
    image_dims = (3, 224, 224)
    result = img_recon.image_recognition(
        "flowers", model, map_names, img_path, image_dims
    )
    return {"result": result}


@methods.add
async def dogs(**kwargs):
    log.debug("dogs({})".format(kwargs))
    model = kwargs.get("model", "ResNet18")
    map_names = dogs_map_names
    img_path = kwargs.get("img_path", None)
    if img_path is None:
        raise InvalidParams('"img_path" is required')
    image_dims = (3, 224, 224)

    result = img_recon.image_recognition("dogs", model, map_names, img_path, image_dims)
    return {"result": result}


@methods.add
async def cars(**kwargs):
    log.debug("cars({})".format(kwargs))
    return {"result": '"cars" Not Implemented yet!'}


async def json_rpc_handle(request):
    request = await request.text()
    response = await methods.dispatch(request, trim_log_values=True)
    if response.is_notification:
        return web.Response()
    else:
        return web.json_response(response, status=response.http_status)


if __name__ == "__main__":
    parser = service.common.common_parser(__file__)
    args = parser.parse_args(sys.argv[1:])
    service.common.main_loop(json_rpc_handle, args)
