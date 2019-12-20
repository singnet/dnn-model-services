import os
import base64
import datetime
import hashlib
import shutil
import requests
import traceback

from spleeter.separator import Separator

import logging

logging.basicConfig(level=10, format="%(asctime)s - [%(levelname)8s] - %(name)s - %(message)s")
log = logging.getLogger("sound_spleeter")


def spleeter(response, audio_url=None, audio=None):
    try:
        response["vocals"] = b"Fail"
        response["accomp"] = b"Fail"

        audio_data = audio
        if audio_url:
            # Link
            if "http://" in audio_url or "https://" in audio_url:
                header = {'User-Agent': 'Mozilla/5.0 (Windows NT x.y; Win64; x64; rv:9.0) Gecko/20100101 Firefox/10.0'}
                # Check if audio file has less than 5Mb
                r = requests.head(audio_url, headers=header, allow_redirects=True)
                size = r.headers.get('content-length', 0)
                size = int(size) / float(1 << 20)
                log.info("File size: {:.2f} Mb".format(size))
                if size > 5:
                    response["vocals"] = b"Input audio file is too large! (max 5Mb)"
                    response["accomp"] = b"Fail"
                    return
                r = requests.get(audio_url, headers=header, allow_redirects=True)
                audio_data = r.content
            # Base64
            elif len(audio_url) > 500:
                audio_data = base64.b64decode(audio_url)

        log.info("Preparing directories...")
        tmp_dir = "/tmp/" + generate_uid() + "/"
        if not os.path.exists(tmp_dir):
            os.makedirs(tmp_dir)

        audio_path = generate_uid() + ".audio"
        with open(tmp_dir + audio_path, "wb") as f:
            f.write(audio_data)

        log.info("Preparing Spleeter...")
        # Using embedded configuration.
        separator = Separator("spleeter:2stems")
        separator.separate_to_file(tmp_dir + audio_path, tmp_dir)

        if os.path.exists(tmp_dir + audio_path):
            os.remove(tmp_dir + audio_path)

        # Getting the output files content
        out_dir = tmp_dir + audio_path.replace(".audio", "") + "/"
        output_vocals = out_dir + "vocals.wav"
        with open(output_vocals, "rb") as fv:
            vocals = fv.read()
        output_accomp = out_dir + "accompaniment.wav"
        with open(output_accomp, "rb") as fa:
            accomp = fa.read()

        # Deleting the files output directory
        shutil.rmtree(tmp_dir)

        response["vocals"] = vocals
        response["accomp"] = accomp
        return

    except Exception as e:
        log.error(e)
        traceback.print_exc()
        return


def generate_uid():
    # Setting a hash accordingly to the timestamp
    seed = "{}".format(datetime.datetime.now())
    m = hashlib.sha256()
    m.update(seed.encode("utf-8"))
    m = m.hexdigest()
    # Returns only the first and the last 10 hex
    return m[:10] + m[-10:]
