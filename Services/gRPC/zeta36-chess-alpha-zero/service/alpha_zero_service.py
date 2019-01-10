import os
import sys
import datetime
import hashlib
import logging
import traceback

import grpc
import concurrent.futures as futures

# Using session to consume less GPU memory
import tensorflow as tf
tf_session_config = tf.ConfigProto()
tf_session_config.gpu_options.allow_growth = True
sess = tf.Session(config=tf_session_config)

sys.path.append(os.path.join(os.getcwd(), 'chess-alpha-zero', 'src'))

from chess_zero.config import Config, PlayWithHumanConfig
from chess_zero.env.chess_env import ChessEnv
from chess_zero.agent.player_chess import ChessPlayer
from chess_zero.agent.model_chess import ChessModel
from chess_zero.lib.model_helper import load_best_model_weight

import service.common
from service.alpha_zero import AlphaZeroClass

# Importing the generated codes from buildproto.sh
import service.service_spec.alpha_zero_pb2_grpc as grpc_bt_grpc
from service.service_spec.alpha_zero_pb2 import Output

logging.basicConfig(level=10, format="%(asctime)s - [%(levelname)8s] - %(name)s - %(message)s")
log = logging.getLogger("alpha_zero_service")

ALPHA_ZERO_PLAYER = None
CHESS_ENV_DICT = dict()


# Create a class to be added to the gRPC server
# derived from the protobuf codes.
class AlphaZeroServicer(grpc_bt_grpc.AlphaZeroServicer):
	def __init__(self):
		self.uid = ""
		self.move = ""
		self.cmd = ""

		self.response = ""

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

			# To respond we need to create a Output() object (from .proto file)
			self.response = Output()

			self.response.uid = self.uid.encode("utf-8")
			self.response.board = ""

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

			msc = AlphaZeroClass(self.move, self.cmd, ALPHA_ZERO_PLAYER, chess_env)

			chess_env, tmp_response = msc.play()
			# Game over
			if chess_env is None:
				del CHESS_ENV_DICT[self.uid]
			else:
				# Update the board state for current UID
				CHESS_ENV_DICT[self.uid] = chess_env

			for idx, line in enumerate(tmp_response["board"]):
				self.response.board += "{}\n".format(line)
			self.response.board = self.response.board.encode("utf-8")
			self.response.status = tmp_response["status"].encode("utf-8")

			log.debug("play({},{}):\n{}\n{}\n{}".format(
				self.move,
				self.cmd,
				self.response.uid,
				self.response.board,
				self.response.status)
			)

			return self.response

		except Exception as e:
			traceback.print_exc()
			log.error(e)
			self.response = Output()
			self.response.status = "Fail"
			return self.response


def get_player_from_model(config):
	try:
		model = ChessModel(config)
		if not load_best_model_weight(model):
			raise RuntimeError("Best model not found!")
		return ChessPlayer(config, model.get_pipes(config.play.search_threads))

	except Exception as e:
		traceback.print_exc()
		log.error(e)
		return None


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

	# Initial Alpha Zero setup
	default_config = Config()
	PlayWithHumanConfig().update_play_config(default_config.play)
	ALPHA_ZERO_PLAYER = get_player_from_model(default_config)

	parser = service.common.common_parser(__file__)
	args = parser.parse_args(sys.argv[1:])
	service.common.main_loop(serve, args)
