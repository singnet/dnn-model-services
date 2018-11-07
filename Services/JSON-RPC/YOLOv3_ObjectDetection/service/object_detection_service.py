import sys
import logging

from aiohttp import web
from jsonrpcserver.aio import methods
from jsonrpcserver.exceptions import InvalidParams

import service.common
from service.object_detection import ObjectDetector
from service import map_names

logging.basicConfig(level=10, format="%(asctime)s - [%(levelname)8s] - %(name)s - %(message)s")
log = logging.getLogger("obj_detect_service")


@methods.add
async def version(**kwargs):
    log.debug("version()")
    return {"result": "v0.1"}


@methods.add
async def detect(**kwargs):
    model = kwargs.get("model", "yolov3")
    confidence = kwargs.get("confidence", "0.7")
    img_path = kwargs.get("img_path", None)
    if img_path is None:
        raise InvalidParams("\"img_path\" is required")
    log.debug("detect({},{},{})".format(model, confidence, len(img_path)))
    objd = ObjectDetector(model, confidence, map_names, img_path)

    return {"result": objd.detect()}


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
