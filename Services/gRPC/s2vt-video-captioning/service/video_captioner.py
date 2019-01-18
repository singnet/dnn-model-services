import os
import shutil
import time
import logging
import requests

from utils.extract_features import extractor
from utils.s2vt_captioner import get_captions
from utils.video_tools import get_video_frames, get_video_length

logging.basicConfig(level=10, format="%(asctime)s - [%(levelname)8s] - %(name)s - %(message)s")
log = logging.getLogger("video_cap_service")


class VideoCaptioner:
    def __init__(self, url, uid, start_time, stop_time, pace, batch_size):
        self.url = url
        self.video_path = ""
        self.uid = uid
        self.video_folder = "./service/utils/videos/{}".format(self.uid)
        self.start_time = start_time
        self.stop_time = stop_time
        self.pace = pace
        self.batch_size = batch_size

        self.response = dict()

    # Returns the caption in SRT format.
    # 1
    # [hours]:[minutes]:[seconds],[milliseconds] --> [hours]:[minutes]:[seconds],[milliseconds]
    # Caption
    def _create_srt(self, s):
        if self.stop_time == 0:
            self.stop_time = get_video_length(self.video_path)
        start_caption = time.strftime("%H:%M:%S,00", time.gmtime(int(self.start_time)))
        stop_caption = time.strftime("%H:%M:%S,00", time.gmtime(int(self.stop_time)))
        if s:
            s = s[0].split("\t")[-1].replace("\n", "")
        return "1\n{} --> {}\n{}".format(start_caption, stop_caption, s)

    # Downloads the video from URL.
    def _download_video(self):
        try:
            # Link
            if "http://" in self.url or "https://" in self.url:
                header = {
                    "User-Agent": "Mozilla/5.0 (Windows NT x.y; Win64; x64; rv:9.0) Gecko/20100101 Firefox/10.0"}
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

    # Main method, it gets the url, start_time and stop_time and returns a Caption.
    def get_video_captions(self):
        if not os.path.exists("./service/utils/videos"):
            os.makedirs("./service/utils/videos")
        if not os.path.exists(self.video_folder):
            os.makedirs(self.video_folder)

        self.response = {"Caption": "Fail"}
        try:
            # Download the video from YouTube.
            if self._download_video():
                # Get all frames within interval start_time and stop_time.
                ok, frames_list = get_video_frames(self.video_path,
                                                   self.video_folder,
                                                   self.start_time*1000,
                                                   self.stop_time*1000,
                                                   self.pace)
                if ok:
                    # If batch_size == 0, use length of frame_list.
                    if self.batch_size == 0:
                        self.batch_size = len(frames_list)
                        if self.batch_size > 60:
                            log.error("batch_size is too high! (max: 20s)")
                            self.response["Caption"] = "Fail: batch_size is too high! (max: 20s)"

                    # Extracts features from frames.
                    features_file = "{}/output_{}.csv".format(self.video_folder, self.uid)
                    if extractor("./service/utils/data/VGG_ILSVRC_16_layers.caffemodel",
                                 "./service/utils/data/VGG_ILSVRC_16_layers_deploy.prototxt",
                                 frames_list,
                                 features_file,
                                 self.batch_size):
                        model_name = "s2vt_vgg_rgb"
                        output_path = "{}/{}_captions.txt".format(self.video_folder, self.uid)
                        # Gets caption from frames (featured).
                        get_captions(model_name, features_file, output_path)
                        with open(output_path, "r") as f:
                            result = f.readlines()
                        self.response["Caption"] = self._create_srt(result)

        except Exception as e:
            log.error(e)
            self.response["Caption"] = "Fail"

        # Deletes video folder.
        if os.path.exists(self.video_folder):
            shutil.rmtree(self.video_folder)

        return self.response
