import os
import sys
import datetime
import hashlib
import logging
import traceback

import multiprocessing

import grpc
import concurrent.futures as futures

import service.common

sys.path.append(os.path.join(os.getcwd(), 'chess-alpha-zero', 'src'))
from chess_zero.env.chess_env import ChessEnv

# Importing the generated codes from buildproto.sh
import service.service_spec.alpha_zero_pb2_grpc as grpc_bt_grpc
from service.service_spec.alpha_zero_pb2 import Output

logging.basicConfig(level=10, format="%(asctime)s - [%(levelname)8s] - %(name)s - %(message)s")
log = logging.getLogger("alpha_zero_service")

CHESS_ENV_DICT = dict()


def mp_play(move, cmd, chess_env, return_dict):
    from service.alpha_zero import AlphaZeroClass
    msc = AlphaZeroClass(move, cmd, chess_env)
    return_dict["response"] = msc.play()


# Create a class to be added to the gRPC server
# derived from the protobuf codes.
class AlphaZeroServicer(grpc_bt_grpc.AlphaZeroServicer):
    def __init__(self):
        self.uid = ""
        self.move = ""
        self.cmd = ""
        log.debug("AlphaZeroServicer created")

    # The method that will be exposed to the snet-cli call command.
    # request: incoming data
    # context: object that provides RPC-specific information (timeout, etc).
    def play(self, request, context):

        try:
            # In our case, request is a Input() object (from .proto file)
            self.uid = request.uid
            # Get a random generated UID (hash)
            if self.uid not in CHESS_ENV_DICT:
                if self.uid == "":
                    self.uid = generate_uid()
                chess_env = ChessEnv().reset()
                log.debug("UID created: {}".format(self.uid))
            else:
                chess_env = CHESS_ENV_DICT[self.uid]
                log.debug("UID exists: {}".format(self.uid))

            # Check if a command was sent.
            self.cmd = request.cmd
            if self.cmd == "finish":
                log.debug("CMD [finish]: {}".format(self.uid))
                if self.uid in CHESS_ENV_DICT:
                    del CHESS_ENV_DICT[self.uid]
                    self.response.status = "game_over by finish command".encode("utf-8")
                else:
                    self.response.status = "no game for this UID: {}".format(self.uid).encode("utf-8")
                return self.response
            elif self.cmd == "restart":
                chess_env = ChessEnv().reset()
                log.debug("CMD [restart]: {}".format(self.uid))

            self.move = request.move

            manager = multiprocessing.Manager()
            return_dict = manager.dict()

            p = multiprocessing.Process(target=mp_play, args=(self.move,
                                                              self.cmd,
                                                              chess_env,
                                                              return_dict))
            p.start()
            p.join()

            chess_env, response = return_dict.get("response", (None, None))
            if not response or "error" in response:
                error_msg = response.get("error", None) if response else None
                log.error(error_msg)
                context.set_details(error_msg)
                context.set_code(grpc.StatusCode.INTERNAL)
                return Output()

            # Game over
            if chess_env is None:
                del CHESS_ENV_DICT[self.uid]
            else:
                # Update the board state for current UID
                CHESS_ENV_DICT[self.uid] = chess_env

            board = ""
            for idx, line in enumerate(response["board"]):
                board += "{}\n".format(line)

            log.debug("play({},{}):\n{}\n{}\n{}".format(
                self.move,
                self.cmd,
                self.uid,
                board,
                response["status"]))
            return Output(uid=self.uid, board=board, status=response["status"])

        except Exception as e:
            traceback.print_exc()
            log.error(e)
            return Output(status="Fail")


def generate_uid():
    # Setting a hash accordingly to the timestamp
    seed = "{}".format(datetime.datetime.now())
    m = hashlib.sha256()
    m.update(seed.encode("utf-8"))
    m = m.digest().hex()
    # Returns only the first and the last 10 hex
    return m[:10] + m[-10:]


# The gRPC serve function.
#
# Params:
# max_workers: pool of threads to execute calls asynchronously
# port: gRPC server port
#
# Add all your classes to the server here.
# (from generated .py files by protobuf compiler)
def serve(max_workers=10, port=7777):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))
    grpc_bt_grpc.add_AlphaZeroServicer_to_server(AlphaZeroServicer(), server)
    server.add_insecure_port("[::]:{}".format(port))
    return server


if __name__ == "__main__":
    """
    Runs the gRPC server to communicate with the Snet Daemon.
    """
    parser = service.common.common_parser(__file__)
    args = parser.parse_args(sys.argv[1:])
    service.common.main_loop(serve, args)
