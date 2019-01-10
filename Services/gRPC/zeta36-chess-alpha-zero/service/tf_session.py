import os
import sys
import logging
import traceback

sys.path.append(os.path.join(os.getcwd(), 'chess-alpha-zero', 'src'))

logging.basicConfig(level=10, format="%(asctime)s - [%(levelname)8s] - %(name)s - %(message)s")
log = logging.getLogger("tf_session")


class TFSession:
	def __init__(self):
		# Tensorflow session
		import tensorflow as tf
		log.debug("Initializing Tensorflow session...")
		tf_session_config = tf.ConfigProto()
		tf_session_config.gpu_options.allow_growth = True
		self.sess = tf.Session(config=tf_session_config)

		from chess_zero.config import Config, PlayWithHumanConfig
		from chess_zero.env.chess_env import ChessEnv

		self.chess_env_class = ChessEnv

		default_config = Config()
		PlayWithHumanConfig().update_play_config(default_config.play)
		self.alpha_player = self.get_player_from_model(default_config)

	@staticmethod
	def get_player_from_model(config):
		try:
			from chess_zero.agent.player_chess import ChessPlayer
			from chess_zero.agent.model_chess import ChessModel
			from chess_zero.lib.model_helper import load_best_model_weight
			model = ChessModel(config)
			if not load_best_model_weight(model):
				raise RuntimeError("Best model not found!")
			return ChessPlayer(config, model.get_pipes(config.play.search_threads))

		except Exception as e:
			traceback.print_exc()
			log.error(e)
			return None

	def close(self):
		if self.sess:
			log.debug("Closing Tensorflow session...")
			self.sess.close()


def bridge():
	tf_session = TFSession()

