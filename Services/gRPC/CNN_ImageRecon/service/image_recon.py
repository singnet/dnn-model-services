# Import CNTK
import cntk

import numpy as np
from PIL import Image
import os
import time
import requests
import base64
import traceback

resources_root = os.path.join("..", "..", "..", "CNTK", "Resources")


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
        print("Could not open (skipping file): ", image_path)
        return ["None"]


def image_recognition(method, model, map_names, img_path, image_dims):
    try:
        # Link
        if "http://" in img_path or "https://" in img_path:
            r = requests.get(img_path, allow_redirects=True)
            with open("temp_img.jpg", "wb") as my_f:
                my_f.write(r.content)
                img_path = "temp_img.jpg"

        # Base64
        elif len(img_path) > 500:
            imgdata = base64.b64decode(img_path)
            filename = "temp_img.jpg"
            with open(filename, "wb") as f:
                f.write(imgdata)
                img_path = "temp_img.jpg"

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
        os.remove("temp_img.jpg")
        return {"delta_time": "{:.4f}".format(delta_time), "top_5": top_5_dict}

    except Exception as e:
        traceback.print_exc()
        return {"delta_time": "Fail", "top_5": "Fail"}
