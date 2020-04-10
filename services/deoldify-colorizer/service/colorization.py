import os
import sys
import requests
import hashlib
import datetime
import base64
from pathlib import Path
from shutil import copyfile
import logging
import traceback

SERVICE_FOLDER = Path(__file__).absolute().parent.parent
sys.path.insert(0, str(SERVICE_FOLDER.joinpath("DeOldify")))
from deoldify.visualize import get_artistic_image_colorizer


logging.basicConfig(level=10, format="%(asctime)s - [%(levelname)8s] - %(name)s - %(message)s")
log = logging.getLogger("colorization")


class Colorization:
    def __init__(self, img_input, render_factor=35):
        self.img_input = img_input
        self.render_factor = render_factor if render_factor else 35
        self.response = dict()
    
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
            input_file = "/tmp/" + uid + "_input.png"

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

            resources_root = SERVICE_FOLDER.parent.parent.joinpath("utils", "Resources", "Models", "DeOldify")

            # from DeOldify
            if not os.path.exists(SERVICE_FOLDER.joinpath("test_images")):
                os.makedirs(SERVICE_FOLDER.joinpath("test_images"))
            if not os.path.exists(SERVICE_FOLDER.joinpath("resource_images")):
                os.makedirs(SERVICE_FOLDER.joinpath("resource_images"))
            if not os.path.exists(SERVICE_FOLDER.joinpath("resource_images/watermark.png")):
                copyfile(resources_root.joinpath("models/watermark.png"),
                         SERVICE_FOLDER.joinpath("resource_images/watermark.png"))

            colorizer = get_artistic_image_colorizer(root_folder=resources_root,
                                                     weights_name="ColorizeArtistic_gen",
                                                     results_dir="/tmp/")
            output_img = colorizer.plot_transformed_image(path=input_file,
                                                          render_factor=self.render_factor,
                                                          watermarked=True)

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
            self.response = {"img_colorized": "Fail", "error": str(e)}
            return self.response
