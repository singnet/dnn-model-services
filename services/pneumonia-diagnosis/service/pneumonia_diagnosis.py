import os
import requests
import logging
import base64
import datetime
import hashlib
import traceback

import numpy as np
from keras.models import load_model
from keras.preprocessing.image import img_to_array
from keras.optimizers import SGD
from keras import backend as K

import cv2


logging.basicConfig(level=10, format="%(asctime)s - [%(levelname)8s] - "
                                     "%(name)s - %(message)s")
log = logging.getLogger("pneumonia_diagnosis")

resources_root = os.path.join("..", "..", "utils", "Resources")


def diagnosis(img_path):
    try:
        tmp_img_file = generate_uid() + ".jpg"
        # Link
        if "http://" in img_path or "https://" in img_path:
            header = {
                'User-Agent': 'Mozilla/5.0 '
                              '(Windows NT x.y; Win64; x64; rv:9.0) '
                              'Gecko/20100101 Firefox/10.0'}
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

        model_file = os.path.join(resources_root,
                                  "Models", "PneumoniaModel.h5")

        K.clear_session()

        img_width, img_height = 128, 128
        model = load_model(model_file)
        model.compile(loss="binary_crossentropy",
                      optimizer=SGD(lr=0.001, momentum=0.9),
                      metrics=["accuracy"])

        image = cv2.imread(img_path)
        image = cv2.resize(image, (img_width, img_height))

        image = image.astype("float") / 255.0
        image = img_to_array(image)
        image = np.expand_dims(image, axis=0)

        result = model.predict(image)
        pred = np.argmax(result, axis=1)

        K.clear_session()
        
        if os.path.exists(tmp_img_file):
            os.remove(tmp_img_file)

        if pred[0] == 0:
            return "Normal"
        return "Pneumonia"

    except Exception as e:
        log.error(e)
        traceback.print_exc()
        return "Normal"


def generate_uid():
    # Setting a hash accordingly to the timestamp
    seed = "{}".format(datetime.datetime.now())
    m = hashlib.sha256()
    m.update(seed.encode("utf-8"))
    m = m.hexdigest()
    # Returns only the first and the last 10 hex
    return m[:10] + m[-10:]
