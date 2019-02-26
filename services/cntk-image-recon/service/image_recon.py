# Import CNTK
import cntk

import numpy as np
from PIL import Image
import os
import time
import requests
import base64
import logging
import datetime
import hashlib
import traceback

logging.basicConfig(level=10, format="%(asctime)s - [%(levelname)8s] - %(name)s - %(message)s")
log = logging.getLogger("cntk_image_recon")

resources_root = os.path.join("..", "..", "utils", "Resources")


# Evaluates a single image using the re-trained model
def eval_single_image(loaded_model, image_path, image_dims):
    # Load and format image (resize, RGB -> BGR, CHW -> HWC)
    try:
        img = Image.open(image_path)

        if image_path.endswith("png"):
            temp = Image.new("RGB", img.size, (255, 255, 255))
            temp.paste(img, img)
            img = temp
        resized = img.resize((image_dims[2], image_dims[1]), Image.ANTIALIAS)
        bgr_image = np.asarray(resized, dtype=np.float32)[..., [2, 1, 0]]
        hwc_format = np.ascontiguousarray(np.rollaxis(bgr_image, 2))

        # Compute model output
        arguments = {loaded_model.arguments[0]: [hwc_format]}
        output = loaded_model.eval(arguments)

        # Return softmax probabilities
        sm = cntk.softmax(output[0])
        return sm.eval()

    except FileNotFoundError:
        log.error("Could not open (skipping file): ", image_path)
        return ["None"]


def image_recognition(method, model, map_names, img_path, image_dims):
    try:
        tmp_img_file = generate_uid() + ".jpg"
        # Link
        if "http://" in img_path or "https://" in img_path:
            header = {'User-Agent': 'Mozilla/5.0 (Windows NT x.y; Win64; x64; rv:9.0) Gecko/20100101 Firefox/10.0'}
            r = requests.get(img_path, headers=header, allow_redirects=True)
            with open(tmp_img_file, "wb") as my_f:
                my_f.write(r.content)
                img_path = tmp_img_file

        # Base64
        elif len(img_path) > 500:
            img_data = base64.b64decode(img_path)
            with open(tmp_img_file, "wb") as f:
                f.write(img_data)
                img_path = tmp_img_file

        model_file = os.path.join(resources_root, "Models", "{}_{}_20.model".format(method, model))

        if model == "AlexNet":
            image_dims = (3, 227, 227)
        elif model == "InceptionV3":
            image_dims = (3, 299, 299)

        start_time = time.time()
        trained_model = cntk.load_model(model_file)
        probs = eval_single_image(trained_model, img_path, image_dims)
        top_5_dict = {}
        p_array = probs.argsort()[-5:][::-1]
        for i, prob in enumerate(p_array):
            perc = probs[prob] * 100
            top_5_dict[i + 1] = "{0:05.2f}%: {1}".format(perc, map_names[int(prob)])

        delta_time = time.time() - start_time
        if os.path.exists(tmp_img_file):
            os.remove(tmp_img_file)
        return {"delta_time": "{:.4f}".format(delta_time), "top_5": top_5_dict}

    except Exception as e:
        log.error(e)
        traceback.print_exc()
        return {"delta_time": "Fail", "top_5": "Fail"}


def generate_uid():
    # Setting a hash accordingly to the timestamp
    seed = "{}".format(datetime.datetime.now())
    m = hashlib.sha256()
    m.update(seed.encode("utf-8"))
    m = m.hexdigest()
    # Returns only the first and the last 10 hex
    return m[:10] + m[-10:]
