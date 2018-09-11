import os
import time
import requests
import base64
import logging
import traceback
import ast

from service.snet_control import SnetInstance
import service.image_utils as imgutils

logging.basicConfig(
    level=10, format="%(asctime)s - [%(levelname)8s] - %(name)s - %(message)s"
)
log = logging.getLogger("DetectRecon")


class DetectRecon(SnetInstance):
    """
    Calls the ObjectDetection Service, parses its output and creates the images with the bboxes.
    Then executes the ImageRecon Service for each bbox image to get its classification.
    Finally returns the original image with the bboxes and the classification (with the confidence)
    of each one.
    """

    def __init__(self, map_names, img_path):
        super(DetectRecon, self).__init__()
        self.map_names = map_names
        self.img_path = img_path
        log.info("DetectRecon created!")

    def detect_recon(self):
        """
        The core method to call services and return the final output.
        """
        try:
            # Check if the paramethers of the Services were set.
            if not self.snet_call_params:
                log.error("Please, set up the service call params.")
                return {}

            start_time = time.time()

            if not os.path.exists("temp"):
                os.makedirs("temp")

            # Link
            if "http://" in self.img_path or "https://" in self.img_path:
                r = requests.get(self.img_path, allow_redirects=True)
                with open("./temp/temp_img.jpg", "wb") as my_f:
                    my_f.write(r.content)
                    self.img_path = "./temp/temp_img.jpg"

            # Base64
            elif len(self.img_path) > 500:
                imgutils.save64(self.img_path)
                self.img_path = "./temp/temp_img.jpg"

            name = "objDetect"
            if name in self.snet_call_params:
                log.info("Calling {}...".format(name))
                self.snet_reset_flags()
                call_params = self.snet_call_params["objDetect"]
                if self.snet_call_service(name, call_params):
                    self.snet_call_res_json[name] = self.snet_response
                else:
                    self.snet_call_res_json[name] = {""}

            result = {}
            result["boxes"] = "Fail"
            result["class_ids"] = "Fail"
            result["confidences"] = "Fail"
            result["top_1_list"] = []

            ###########
            #
            # Crop all bboxes received from the ObjectDetection Service
            # and then send each one for the Image Recognition Service
            #
            ###########
            if self.snet_call_res_json[name] != {""}:
                base64_img = self.snet_call_res_json[name]["response"]["img_base64"]
                imgutils.save64(base64_img, "./temp/objdetect_output.jpg")

                bboxes = self.snet_call_res_json[name]["response"]["boxes"]
                class_ids = self.snet_call_res_json[name]["response"]["class_ids"]
                confidences = self.snet_call_res_json[name]["response"]["confidences"]
                if bboxes == "Fail":
                    log.error("ObjectDetector failed!")
                else:
                    bboxes = ast.literal_eval(bboxes)
                    log.info("Found {} bbox(es)!".format(len(bboxes)))
                    result["boxes"] = bboxes
                    result["class_ids"] = ast.literal_eval(class_ids)
                    result["confidences"] = ast.literal_eval(confidences)
                    for idx, box in enumerate(bboxes):
                        class_id = int(result["class_ids"][idx])
                        if class_id not in [15, 16, 17, 18, 19]:
                            log.info(
                                "Class '{}' not in classification range!".format(
                                    self.map_names[class_id]
                                )
                            )
                            continue
                        log.info("Cropping bbox {}/{}...".format(idx + 1, len(bboxes)))
                        coords = (box[0], box[1], box[0] + box[2], box[1] + box[3])

                        base64_bbox = imgutils.crop_image(
                            self.img_path, coords, "base64"
                        )

                        # Setting ImageRecon Service params
                        name = "imgRecon"
                        agent_addr = "0x9211Ca9A96063401BaAC5cafE85efC4024325279"
                        method = "dogs"
                        json_txt = '{"model": "%s", "img_path": "%s"}' % (
                            "ResNet152",
                            base64_bbox,
                        )
                        self.snet_set_params(name, agent_addr, method, json_txt)
                        self.snet_reset_flags()

                        log.info("Calling {}...".format(name))
                        call_params = self.snet_call_params["imgRecon"]
                        if self.snet_call_service(name, call_params):
                            self.snet_call_res_json[name] = self.snet_response
                            top_5 = self.snet_call_res_json[name]
                            if top_5 != "Fail":
                                d_tmp = ast.literal_eval(
                                    self.snet_call_res_json[name]["response"]["top_5"]
                                )
                                top_1 = d_tmp[1]
                                crop_class_filename = (
                                    top_1.replace(" ", "")
                                    .replace("%", "")
                                    .replace(":", "_")
                                )

                                log.info("Saving image...".format(name))
                                imgutils.save64(
                                    base64_bbox,
                                    "./temp/{}.jpg".format(crop_class_filename),
                                )
                                result["top_1_list"].append(top_1)
                            else:
                                log.error("ImageRecon failed!")
                        else:
                            log.info("Nothing has returned from snet call!")
                            self.snet_call_res_json[name] = {""}

            else:
                log.error("ObjectDetector is not responding!")

            if os.path.exists("temp_img.jpg"):
                os.remove("temp_img.jpg")

            delta_time = time.time() - start_time
            result["delta_time"] = delta_time

            return result

        except Exception as e:
            traceback.print_exc()
            return {"delta_time": "Fail"}
