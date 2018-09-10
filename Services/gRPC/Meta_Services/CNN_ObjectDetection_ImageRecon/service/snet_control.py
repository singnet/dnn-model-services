import pathlib
import subprocess
import logging
import threading
import traceback
import yaml
import time
import os


logging.basicConfig(
    level=10, format="%(asctime)s - [%(levelname)8s] - %(name)s - %(message)s"
)
log = logging.getLogger("snetControl")


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
        self.snet_waiting_response = 100
        self.snet_waiting_busy = 30
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
                    if count > self.snet_waiting_response:
                        break

                if self.snet_response:
                    return True
                else:
                    if self.snet_error == 1:
                        log.info(
                            "Waiting 30s for the previous transaction be completed..."
                        )
                        time.sleep(self.snet_waiting_busy)
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
                "Running 'snet client call {}' with args:\n{}".format(method, cmd_list)
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
                        "Snet client call returned an error: {}!".format(
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
