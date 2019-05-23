import os
import logging
import requests
import pathlib
import shutil

import subprocess
import signal

import glob
import tarfile
from datetime import datetime, timedelta

import time
from threading import Thread

# TensorFlow and TF-Hub modules.
import tensorflow as tf

tf.logging.set_verbosity(tf.logging.ERROR)

logging.basicConfig(level=10, format="%(asctime)s - [%(levelname)8s] - "
                                     "%(name)s - %(message)s")
log = logging.getLogger("deepfakes_faceswap")


class FaceSwapper:
    def __init__(self, uid, model_url, video_a, video_b):
        self.uid = uid
        self.model_url = model_url
        self.video_a_url = video_a
        self.video_b_url = video_b

        self.service_folder = pathlib.Path(__file__).absolute().parent.parent
        self.user_folder = \
            self.service_folder / "data" / "{}".format(self.uid)
        self.video_a_folder = self.user_folder / "A"
        self.video_b_folder = self.user_folder / "B"
        self.video_model_folder = self.user_folder / "model"
        self.video_out_folder = self.user_folder / "output"

        self.model_path = ""
        self.video_a_path = ""
        self.video_b_path = ""
        
        self.p = None
        self.p_code = -1

        self.error = ""
        self.response = dict()

    # Downloads file from URL.
    def _download_data(self, source, file_name, max_size=20, force=False):
        try:
            local_path = self.user_folder / file_name
            if not os.path.exists(str(local_path)) or force:
                log.info("Downloading: {}".format(source))
                # Downloading content
                if "http://" in source or "https://" in source:
                    header = {
                        "User-Agent":
                        "Mozilla/5.0 (Windows NT x.y; Win64; x64; rv:9.0) "
                        "Gecko/20100101 Firefox/10.0"
                    }
                    # Check if file has less than max_size
                    r = requests.head(source,
                                      headers=header,
                                      allow_redirects=True)
                    size = r.headers.get('content-length', 0)
                    size = int(size) / float(1 << 20)
                    log.info("File size: {:.2f} Mb".format(size))
                    if size <= max_size:
                        r = requests.get(source,
                                         headers=header,
                                         allow_redirects=True)
                        with open(str(local_path), "wb") as my_f:
                            my_f.write(r.content)
                    else:
                        self.error += "[Fail] {} is too large (>{}Mb).".format(
                            source.split("/")[-1],
                            max_size)
                else:
                    self.error += "[Fail] Not a valid url = {}".format(
                        source.split("/")[-1])
            if self.error:
                return False, self.error
            return True, local_path

        except Exception as e:
            log.error(e)
            return False, str(e)
    
    def _run_proc(self, cmd):
        self.p = subprocess.Popen(cmd, cwd=str(self.service_folder))
        self.p.wait()
        if self.p.returncode and self.p.returncode != 0:
            self.p_code = 1
        else:
            self.p_code = 0

    def _run_with_timeout(self, cmd, timeout):
        th = Thread(target=self._run_proc, daemon=True, args=(cmd, ))
        th.start()

        count = 0
        while count < timeout:
            count += 1
            time.sleep(1)
            # Error
            if self.p_code == 1:
                log.error("Process failed!")
                self.p = None
                self.p_code = -1
                return False
            # OK
            elif self.p_code == 0:
                self.p = None
                self.p_code = -1
                return True

        if count >= timeout:
            if isinstance(self.p, subprocess.Popen):
                log.error("Killing process {}...".format(self.p.pid))
                # Have to send SIGKILL for other spawned processes too.
                for i in range(5):
                    try:
                        os.kill(self.p.pid + i, signal.SIGKILL)
                    except Exception:
                        pass
                log.error("Waiting 10s after SIGKILL signal...")
                time.sleep(10)
            self.p = None
            self.p_code = -1
            return False
        return True

    @staticmethod
    def _delete_old_files(folder):
        try:
            for file_path in glob.iglob("{}/*".format(folder), recursive=True):
                file_ts = datetime.fromtimestamp(os.path.getmtime(file_path))
                if datetime.now() - file_ts > timedelta(hours=24):
                    log.info("Deleting old file: {}".format(file_path))
                    os.remove(file_path)
            return True
        except Exception as e:
            log.error(e)
            return False

    @staticmethod
    def _safe_extract_tar(tar_file_path, dest_dir):
        with tarfile.open(str(tar_file_path), "r:gz") as tar:
            for m in tar.getmembers():
                if not m.isfile() or os.path.dirname(m.name) != "":
                    return False, "Invalid Tarfile content."
            tar.extractall(str(dest_dir))
        return True, ""
    
    def _compress_and_publish(self, model=False):
        if model:
            file_list = glob.glob(
                str(self.video_model_folder) + "/*.h5")
            file_list.extend(glob.glob(
                str(self.video_model_folder) + "/*.json"))
            tar_file_name = "{}_model.tgz".format(self.uid)
            tar_file_path = self.video_model_folder / tar_file_name
            with tarfile.open(str(tar_file_path), "w:gz") as tar:
                for idx, f in enumerate(file_list):
                    tar.add(f, arcname=f.split("/")[-1])
    
            shutil.move(str(tar_file_path),
                        "/opt/storage/DeepfakesFaceswap/Output/{}".format(
                            tar_file_name))
        else:
            video_file = self.user_folder / "{}.mp4".format(self.uid)
            tar_file_name = "{}_video.tgz".format(self.uid)
            tar_file_path = self.video_model_folder / tar_file_name
            with tarfile.open(str(tar_file_path), "w:gz") as tar:
                tar.add(str(video_file),
                        arcname=str(video_file).split("/")[-1])
    
            shutil.move(str(tar_file_path),
                        "/opt/storage/DeepfakesFaceswap/Output/{}".format(
                            tar_file_name))

        # Removing old files from data/ (> 24h)
        self._delete_old_files(self.service_folder / "data")

        # Removing old files from storage/ (> 24h)
        self._delete_old_files("/opt/storage/DeepfakesFaceswap/Output")

        return "http://52.38.111.172:7007/" \
               "DeepfakesFaceswap/Output/" \
               "{}".format(tar_file_name)

    # Main method, it downloads the videos input from URL,
    # extract frames, train the model on them and
    # convert video A into a new video swapping faces.
    def faceswap(self, cs, content_id, model=False):
        if not os.path.exists(str(self.user_folder)):
            os.makedirs(str(self.user_folder))

        try:
            if self.model_url:
                cs.update(content_id,
                          message="Downloading Model")
                log.info("Downloading User's Model...")
                # Download the model from URL.
                ok_download, self.model_path = self._download_data(
                    self.model_url,
                    "{}_model.tgz".format(self.uid),
                    max_size=320,
                    force=True)

                cs.update(content_id,
                          message="Extracting Model")
                log.info("Extracting User's Model...")
                ok_extract, self.error = self._safe_extract_tar(
                    self.model_path,
                    self.video_model_folder)

                if not ok_download or not ok_extract:
                    log.error("Error with User's Model!")
                    self.response["error"] = self.error
                    return self.response

            # Download input videos from URLs.
            ok_a, self.video_a_path = self._download_data(self.video_a_url,
                                                          "tmp_video_a.mp4")
            ok_b, self.video_b_path = self._download_data(self.video_b_url,
                                                          "tmp_video_b.mp4")
            if ok_a and ok_b:
                log.info("Extracting frames from Video A...")
                if not os.path.exists(str(self.video_a_folder)):
                    cs.update(content_id,
                              message="Extracting Video A")
                    if not self._run_with_timeout(["python3",
                                                   "faceswap/faceswap.py",
                                                   "extract",
                                                   "-i",
                                                   str(self.video_a_path),
                                                   "-o",
                                                   str(self.video_a_folder)],
                                                  10 * 60):
                        self.error += "Extracting frames from Video A...Fail!"
                log.info("Extracting frames from Video A...Done!")

                log.info("Extracting frames from Video B...")
                if not os.path.exists(str(self.video_b_folder)):
                    cs.update(content_id,
                              message="Extracting Video B")
                    if not self._run_with_timeout(["python3",
                                                   "faceswap/faceswap.py",
                                                   "extract",
                                                   "-i",
                                                   str(self.video_b_path),
                                                   "-o",
                                                   str(self.video_b_folder)],
                                                  10 * 60):
                        self.error += "Extracting frames from Video B...Fail!"
                log.info("Extracting frames from Video B...Done!")

                if model:
                    log.info("Training the Model...")
                    cs.update(content_id,
                              message="Training the Model")
                    if not self._run_with_timeout(
                            ["python3",
                             "faceswap/faceswap.py",
                             "train",
                             "-A",
                             str(self.video_a_folder),
                             "-B",
                             str(self.video_b_folder),
                             "-m",
                             str(self.video_model_folder),
                             "-it", "3000"],
                            70 * 60):
                        self.error += "Training the model...Fail!"
                    log.info("Training the model...Done!")
                    
                    cs.update(content_id,
                              message="Compressing Model")
                    self.response["model"] = self._compress_and_publish(
                        model=True)
                    return self.response

                log.info("Converting Frames...")
                cs.update(content_id,
                          message="Converting Frames")
                if not self._run_with_timeout(["python3",
                                               "faceswap/faceswap.py",
                                               "convert",
                                               "-i",
                                               str(self.video_a_path),
                                               "-o",
                                               str(self.video_out_folder),
                                               "-m",
                                               str(self.video_model_folder)],
                                              10 * 60):
                    self.error += "Converting the model...Fail!"
                log.info("Converting frames...Done!")
                
                log.info("Generating the final video...")
                cs.update(content_id,
                          message="Generating Video")
                if not self._run_with_timeout(["python3",
                                               "faceswap/tools.py",
                                               "effmpeg", "-a", "gen-vid",
                                               "-fps", "30",
                                               "-i",
                                               str(self.video_out_folder),
                                               "-r",
                                               str(self.video_a_path),
                                               "-o",
                                               str(self.user_folder /
                                                   "{}.mp4".format(self.uid))],
                                              10 * 60):
                    self.error += "Generating the final video...Fail!"
                log.info("Generating the final video...Done!")

                cs.update(content_id,
                          message="Compressing Output Video")
                self.response["video"] = self._compress_and_publish()
            else:
                self.response["error"] = self.error

        except Exception as e:
            log.error(e)
            self.response["error"] = "Fail"

        return self.response
