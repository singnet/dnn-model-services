import os
import pathlib
import time
import requests
import base64
import threading
import logging
import subprocess
import traceback
import yaml

logging.basicConfig(
    level=10, format="%(asctime)s - [%(levelname)8s] - %(name)s - %(message)s"
)
log = logging.getLogger("DetectRecon")


class SnetInstance:
    """
    Used to interact with snet (SNET-CLI v0.1.5) script.
    Executes (max=3x) the 'snet client call' command and returns its output.
    """

    def __init__(self):
        # Control variables
        self.snet_attempts = 3
        self.snet_call_params = {}
        self.snet_call_res_json = {}

        # Execution variables
        self.snet_exited = False
        self.snet_pid = 0
        self.snet_error = 0
        self.snet_response = ""

    def snet_reset_flags(self):
        self.snet_exited = False
        self.snet_pid = 0
        self.snet_error = 0
        self.snet_response = ""

    def snet_set_params(self, name, agent_addr, method, method_params):
        self.snet_call_params[name] = {
            "agent_addr": agent_addr,
            "method": method,
            "method_params": method_params,
        }

    def snet_call_service(self, name, call_params):
        try:
            agent_addr = call_params["agent_addr"]
            method = call_params["method"]
            method_params = call_params["method_params"]

            for num_attempt in range(self.snet_attempts):
                snet_th = threading.Thread(
                    target=self.snet_client_call,
                    args=(agent_addr, method, method_params),
                )

                snet_th.daemon = True
                snet_th.start()

                count = 0
                while not self.snet_exited:
                    time.sleep(1)
                    if not count % 5:
                        log.info(
                            "Waiting snet service {}...[Attempt {}]".format(
                                name, num_attempt + 1
                            )
                        )
                    count += 1
                    if count > 100:
                        break

                if self.snet_response:
                    return True
                else:
                    if self.snet_error == 1:
                        log.info(
                            "Waiting 30s for the previous transaction be completed..."
                        )
                        time.sleep(30)
                    log.info(
                        "Trying to call snet service {} again [Attempt {}]".format(
                            name, num_attempt + 1
                        )
                    )
                    self.snet_reset_flags()

            return False

        except Exception as e:
            traceback.print_exc()
            return False

    def snet_client_call(self, agent_addr, method, method_params):
        try:
            cwd = pathlib.Path("./service/model").absolute()
            cmd_list = [
                "snet",
                "client",
                "call",
                "--no-confirm",
                "--max-price",
                "10000000000",
                "--agent-at",
                agent_addr,
                method,
                method_params,
            ]

            log.info(
                "Running 'snet client call {} with args:\n{}'".format(method, cmd_list)
            )

            self.snet_pid = subprocess.Popen(
                cmd_list,
                stdout=subprocess.PIPE,
                stdin=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=1,
                preexec_fn=os.setsid,
                cwd=str(cwd),
            )

            try:
                outs, errs = self.snet_pid.communicate(timeout=90)
                if self.snet_pid.returncode == 0:
                    self.snet_response = yaml.load(outs)
                else:
                    log.error(
                        "Snet client call returned an {} error!".format(
                            self.snet_pid.returncode
                        )
                    )
                    if (
                        b"There is another transaction with same nonce in the queue."
                        in errs
                    ):
                        log.error(
                            "There is another transaction with same nonce in the queue."
                        )
                        self.snet_error = 1
                    self.snet_exited = True
                    return False
            except subprocess.TimeoutExpired:
                self.snet_pid.kill()

            self.snet_exited = True
            return True

        except Exception as e:
            traceback.print_exc()
            self.snet_exited = True
            return False


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

            # Link
            if "http://" in self.img_path or "https://" in self.img_path:
                r = requests.get(self.img_path, allow_redirects=True)
                with open("temp_img.jpg", "wb") as my_f:
                    my_f.write(r.content)
                    self.img_path = "temp_img.jpg"

            # Base64
            elif len(self.img_path) > 500:
                imgdata = base64.b64decode(self.img_path)
                with open("temp_img.jpg", "wb") as f:
                    f.write(imgdata)
                    self.img_path = "temp_img.jpg"

            # Loop throught Services
            for name, call_params in self.snet_call_params.items():
                self.snet_reset_flags()
                log.info("Calling {}...".format(name))
                if self.snet_call_service(name, call_params):
                    self.snet_call_res_json[name] = self.snet_response
                else:
                    self.snet_call_res_json[name] = {""}

            if os.path.exists("temp_img.jpg"):
                os.remove("temp_img.jpg")

            result = {}
            for name, v in self.snet_call_res_json.items():
                result[name] = v

            delta_time = time.time() - start_time
            result["delta_time"] = delta_time

            return result

        except Exception as e:
            traceback.print_exc()
            return {"delta_time": "Fail"}
