import os
import requests
import hashlib
import datetime
import subprocess
import base64
import logging
import traceback

logging.basicConfig(level=10, format="%(asctime)s - [%(levelname)8s] - %(name)s - %(message)s")
log = logging.getLogger("siggraph_colorization")


class Colorization:
    def __init__(self, img_input):
        self.img_input = img_input
        self.response = dict()

    @staticmethod
    def _is_base64(sb):
        try:
            if type(sb) == str:
                sb_bytes = bytes(sb, 'ascii')
            elif type(sb) == bytes:
                sb_bytes = sb
            else:
                raise ValueError("Argument must be string or bytes")
            return base64.b64encode(base64.b64decode(sb_bytes)) == sb_bytes
        except Exception as e:
            log.error("Not Base64: " + str(e))
            return False
    
    @staticmethod
    def _generate_uid():
        # Setting a hash accordingly to the timestamp
        seed = "{}".format(datetime.datetime.now())
        m = hashlib.sha256()
        m.update(seed.encode("utf-8"))
        m = m.hexdigest()
        # Returns only the first and the last 10 hex
        return m[:10] + m[-10:]

    def colorize(self):

        try:
            uid = self._generate_uid()
            input_file = uid + "_input.png"
            output_img = uid + ".png"
            
            # Link
            if "http://" in self.img_input or "https://" in self.img_input:
                log.info("Got an URL, downloading...")
                header = {'User-Agent': 'Mozilla/5.0 (Windows NT x.y; Win64; x64; rv:9.0) Gecko/20100101 Firefox/10.0'}
                r = requests.get(self.img_input, headers=header, allow_redirects=True)
                with open(input_file, "wb") as fd:
                    fd.write(r.content)
                log.info("Done!")
                
            # Base64
            elif len(self.img_input) > 1000:
                log.info("Got a base64 image data, saving...")
                with open(input_file, "wb") as fd:
                    fd.write(base64.b64decode(self.img_input))
                log.info("Done!")

            resources_root = os.path.join("..", "..", "utils", "Resources")
            colorize_model = os.path.join(resources_root, "Models", "colornet.t7")
            p = subprocess.Popen(["th",
                                  "colorize.lua",
                                  input_file,
                                  output_img,
                                  colorize_model])
            p.wait()

            self.response["img_colorized"] = "Fail"
            with open(output_img, "rb") as base64_file:
                self.response["img_colorized"] = base64.b64encode(base64_file.read())

            if os.path.exists(input_file):
                os.remove(input_file)
            if os.path.exists(output_img):
                os.remove(output_img)

            return self.response

        except Exception as e:
            log.error(e)
            traceback.print_exc()
            self.response["img_colorized"] = "Fail"
            return self.response
