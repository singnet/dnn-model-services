import argparse
import os.path

from aiohttp import web

from service import registry


def common_parser(script_name):
    parser = argparse.ArgumentParser(prog=script_name)
    server_name = os.path.splitext(os.path.basename(script_name))[0]
    parser.add_argument(
        "--json-rpc-port",
        help="port to bind jsonrpc service to",
        default=registry[server_name]["jsonrpc"],
        type=int,
        required=False,
    )
    return parser


def main_loop(jsonrpc_handler, args):
    app = web.Application()
    app.router.add_post("/", jsonrpc_handler)
    web.run_app(app, host="127.0.0.1", port=args.json_rpc_port)
