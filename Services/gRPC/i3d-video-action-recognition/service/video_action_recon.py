import os
import shutil
import logging
import requests
import cv2
import numpy as np

# TensorFlow and TF-Hub modules.
import tensorflow as tf
import tensorflow_hub as hub

tf.logging.set_verbosity(tf.logging.ERROR)

logging.basicConfig(level=10, format="%(asctime)s - [%(levelname)8s] - %(name)s - %(message)s")
log = logging.getLogger("video_action_recon")


class VideoActionRecognizer:
    def __init__(self, uid, model, url):
        self.uid = uid
        self.model = model
        self.url = url
        self.video_path = ""
        self.video_folder = "./service/data/videos/{}".format(self.uid)

        self.response = dict()

    # Downloads the video from URL.
    def _download_video(self):
        try:
            # Link
            if "http://" in self.url or "https://" in self.url:
                header = {"User-Agent": "Mozilla/5.0 (Windows NT x.y; Win64; x64; rv:9.0) Gecko/20100101 Firefox/10.0"}
                r = requests.get(self.url, headers=header, allow_redirects=True)
                self.video_path = self.video_folder + "/tmp_video.vid"
                with open(self.video_path, "wb") as my_f:
                    my_f.write(r.content)
                    self.video_path = self.video_folder + "/tmp_video.vid"
            else:
                self.video_path = "Not a valid video url."
                return False
            return True
        except Exception as e:
            log.error(e)
            return False

    @staticmethod
    def _load_video(path, max_frames=0, resize=(224, 224)):
        # Utilities to open video files using CV2
        def _crop_center_square(fr):
            y, x = fr.shape[0:2]
            min_dim = min(y, x)
            start_x = (x // 2) - (min_dim // 2)
            start_y = (y // 2) - (min_dim // 2)
            return fr[start_y:start_y + min_dim, start_x:start_x + min_dim]

        cap = cv2.VideoCapture(path)
        frames = []
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                frame = _crop_center_square(frame)
                frame = cv2.resize(frame, resize)
                frame = frame[:, :, [2, 1, 0]]
                frames.append(frame)

                if len(frames) == max_frames:
                    break
        finally:
            cap.release()
        return np.array(frames) / 255.0

    # Main method, it gets the url, start_time and stop_time and returns a Caption.
    def video_action_recon(self):
        if not os.path.exists("./service/data/videos"):
            os.makedirs("./service/data/videos")
        if not os.path.exists(self.video_folder):
            os.makedirs(self.video_folder)

        self.response["Top5Actions"] = "Fail"
        try:
            # Download the video from YouTube.
            if self._download_video():
                # Get all frames within interval start_time and stop_time.
                # Get the kinetics-600|400 action labels.
                with open("./service/data/label_map_{}.txt".format(self.model)) as f:
                    labels = [line.strip() for line in f.readlines()]
                log.debug("Found %d labels." % len(labels))

                # Get a sample cricket video.
                sample_video = self._load_video(self.video_path)

                # Run the i3d model on the video and print the top 5 actions.
                # First add an empty dimension to the sample video as the model takes as input
                # a batch of videos.
                model_input = np.expand_dims(sample_video, axis=0)

                with tf.device("/device:GPU:0"):
                    # Create the i3d model and get the action probabilities.
                    with tf.Graph().as_default():
                        i3d = hub.Module("https://tfhub.dev/deepmind/i3d-kinetics-{}/1".format(self.model))
                        input_placeholder = tf.placeholder(shape=(None, None, 224, 224, 3), dtype=tf.float32)
                        logits = i3d(input_placeholder)
                        probabilities = tf.nn.softmax(logits)
                        with tf.train.MonitoredSession() as session:
                            [ps] = session.run(probabilities,
                                               feed_dict={input_placeholder: model_input})

                    self.response["Top5Actions"] = ""
                    log.debug("Top 5 actions:")
                    for i in np.argsort(ps)[::-1][:5]:
                        log.debug("{}\t{:.2f}%".format(labels[i], ps[i] * 100))
                        self.response["Top5Actions"] += "{}\t{:.2f}%\n".format(labels[i], ps[i] * 100)

        except Exception as e:
            log.error(e)
            self.response["Top5Actions"] = "Fail"

        # Deletes video folder.
        if os.path.exists(self.video_folder):
            shutil.rmtree(self.video_folder)

        return self.response
