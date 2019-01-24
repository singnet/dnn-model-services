import sys
import subprocess
import logging
import pathlib
import glob
import argparse

from service import registry

logging.basicConfig(level=10, format="%(asctime)s - [%(levelname)8s] - %(name)s - %(message)s")
log = logging.getLogger("run_alpha_zero_service")


def main():
    parser = argparse.ArgumentParser(description="Run services")
    parser.add_argument("--no-daemon", action="store_false", dest="run_daemon", help="do not start the daemon")
    args = parser.parse_args()
    root_path = pathlib.Path(__file__).absolute().parent

    # All services modules go here
    service_modules = ["service.alpha_zero_service"]

    # Call for all the services listed in service_modules
    all_p = start_all_services(root_path, service_modules, args.run_daemon)

    # Wait for all sub processes
    try:
        for p in all_p:
            p.wait()
    except Exception as e:
        log.error(e)
        raise


def start_all_services(cwd, service_modules, run_daemon):
    """
    Loop through all service_modules and start them.
    For each one, an instance of Daemon "snetd" is created.
    snetd will start with configs from "snetd.config.json"
    """
    all_p = []
    for i, service_module in enumerate(service_modules):
        service_name = service_module.split(".")[-1]
        log.info("Launching {} on port {}".format(str(registry[service_name]), service_module))
        all_p += start_service(cwd, service_module, run_daemon)
    return all_p


def start_service(cwd, service_module, run_daemon):
    """
    Starts SNET Daemon ("snetd") and the python module of the service
    at the passed gRPC port.
    """
    all_p = []
    if run_daemon:
        for idx, config_file in enumerate(glob.glob("./snetd_configs/*.json")):
            all_p.append(start_snetd(str(cwd), config_file))
    service_name = service_module.split(".")[-1]
    grpc_port = registry[service_name]["grpc"]
    p = subprocess.Popen([sys.executable, "-m", service_module, "--grpc-port", str(grpc_port)], cwd=str(cwd))
    all_p.append(p)
    return all_p


def start_snetd(cwd, config_file=None):
    """
    Starts the Daemon "snetd":
    """
    cmd = ["snetd", "serve"]
    if config_file:
        cmd = ["snetd", "serve", "--config", config_file]
    return subprocess.Popen(cmd, cwd=str(cwd))


if __name__ == "__main__":
    main()
