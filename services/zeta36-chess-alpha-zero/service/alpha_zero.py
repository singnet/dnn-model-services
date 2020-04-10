import logging
import traceback

# Using session to consume less GPU memory
import tensorflow as tf

tf_session_config = tf.ConfigProto()
tf_session_config.gpu_options.allow_growth = True
sess = tf.Session(config=tf_session_config)

from chess_zero.config import Config, PlayWithHumanConfig
from chess_zero.agent.player_chess import ChessPlayer
from chess_zero.agent.model_chess import ChessModel
from chess_zero.lib.model_helper import load_best_model_weight


logging.basicConfig(level=10, format="%(asctime)s - [%(levelname)8s] - %(name)s - %(message)s")
log = logging.getLogger("alpha_zero")


class AlphaZeroClass:

	def __init__(self, move, cmd, chess_env):
		self.move = move
		self.cmd = cmd
		self.chess_env = chess_env
		self.alpha_player = None
		self.response = dict()

	def create(self):
		# Initial Alpha Zero setup
		default_config = Config()
		PlayWithHumanConfig().update_play_config(default_config.play)
		return self.get_player_from_model(default_config)

	@staticmethod
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

	def play(self):
		try:
			self.alpha_player = self.create()
			if not self.alpha_player:
				return None, {"error": "Error while creating player."}

			# User move
			self.chess_env.step(self.move)
			log.debug("User move: {}".format(self.move))
			pprint_board(self.chess_env.board)

			# Alpha move
			alpha_move = self.alpha_player.action(self.chess_env, False)
			log.debug("Alpha move: {}".format(alpha_move))
			self.chess_env.step(alpha_move)

			self.response["board"] = pprint_board(self.chess_env.board)
			self.response["status"] = "game_running: {}".format(alpha_move)

			if self.chess_env.winner:
				self.response["status"] = "game_over: {}".format(self.chess_env.winner.name)
				log.error("game_over: {}".format(self.chess_env.winner.name))
				return None, self.response

			# Returns the current board and response
			return self.chess_env, self.response

		except Exception as e:
			self.response["status"] = "move_error"
			self.response["board"] = pprint_board(self.chess_env.board)
			self.response["error"] = str(e)
			log.error("move_error: {}".format(e))
			traceback.print_exc()
			return self.chess_env, self.response


# Print the board in a pretty way.
def pprint_board(board):
	ret = []
	board = str(board)
	print_line = "    a b c d e f g h"
	log.debug(print_line)
	ret.append(print_line)
	print_line = "-------------------"
	log.debug(print_line)
	ret.append(print_line)
	lines = board.split("\n")
	for idx, line in enumerate(lines):
		print_line = "{} | {}".format(8 - idx, line)
		log.debug(print_line)
		ret.append(print_line)
	return ret
