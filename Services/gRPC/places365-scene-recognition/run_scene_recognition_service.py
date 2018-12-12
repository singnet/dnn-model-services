import pathlib
import subprocess
import time
import os
import sys
import logging
import threading

from service import registry

logging.basicConfig(level=10, format="%(asctime)s - [%(levelname)8s] - %(name)s - %(message)s")
log = logging.getLogger("run_scene_recognition_service")


def main():

    root_path = pathlib.Path(__file__).absolute().parent

    # All services modules go here
    service_modules = ["service.scene_recognition_service"]

    # Removing all previous snetd .db file
    os.system("rm *.db")

    # Call for all the services listed in service_modules
    start_all_services(root_path, service_modules)

    # Infinite loop to serve the services
    while True:
        try:
            time.sleep(1)
        except Exception as e:
            print("ERROR HERE 1")
            log.error(e)
            exit(0)


def start_all_services(cwd, service_modules):
    """
    Loop through all service_modules and start them.
    For each one, an instance of Daemon 'snetd' is created.
    snetd will start with configs from 'snet_SERVICENAME_config.json'.
    """
    try:
        for i, service_module in enumerate(service_modules):
            server_name = service_module.split(".")[-1]
            log.info("Launching {} on ports {}".format(server_name, str(registry[server_name]["grpc"])))

            process_thread = threading.Thread(target=start_service, args=(cwd, service_module))

            # Bind the thread with the main() to abort it when main() exits.
            process_thread.daemon = True
            process_thread.start()

    except Exception as e:
        print("ERROR HERE 2")
        log.error(e)
        return False
    return True


def start_service(cwd, service_module):
    """
    Starts the python module of the service at the passed JSON-RPC port and
    an instance of 'snetd' for the service.
    """
    start_snetd(str(cwd))

    service_name = service_module.split(".")[-1]
    grpc_port = registry[service_name]["grpc"]
    subprocess.Popen(
        [sys.executable, "-m", service_module, "--grpc-port", str(grpc_port)],
        cwd=str(cwd))


def start_snetd(cwd):
    """
    Starts the Daemon 'snetd'
    """
    cmd = ["snetd", "serve"]
    subprocess.Popen(cmd, cwd=str(cwd))
    return True


if __name__ == "__main__":
    main()
