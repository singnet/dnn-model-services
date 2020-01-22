import sys
import os
import signal
import time
import subprocess
import logging
import pathlib
import glob
import json
import argparse

from service import registry

logging.basicConfig(level=10, format="%(asctime)s - [%(levelname)8s] - %(name)s - %(message)s")
log = logging.getLogger("run_video_cap_service")


def main():
    parser = argparse.ArgumentParser(description="Run services")
    parser.add_argument("--no-daemon", action="store_false", dest="run_daemon", help="do not start the daemon")
    parser.add_argument("--ssl", action="store_true", dest="run_ssl", help="start the daemon with SSL")
    args = parser.parse_args()
    root_path = pathlib.Path(__file__).absolute().parent
    
    # All services modules go here
    service_modules = ["service.video_cap_service"]
    
    # Call for all the services listed in service_modules
    all_p = start_all_services(root_path, service_modules, args.run_daemon, args.run_ssl)
    
    # Continuous checking all subprocess
    try:
        while True:
            for p in all_p:
                p.poll()
                if p.returncode and p.returncode != 0:
                    kill_and_exit(all_p)
            time.sleep(1)
    except Exception as e:
        log.error(e)
        raise


def start_all_services(cwd, service_modules, run_daemon, run_ssl):
    """
    Loop through all service_modules and start them.
    For each one, an instance of Daemon "snetd" is created.
    snetd will start with configs from "snetd.config.json"
    """
    all_p = []
    for i, service_module in enumerate(service_modules):
        service_name = service_module.split(".")[-1]
        log.info("Launching {} on port {}".format(str(registry[service_name]), service_module))
        all_p += start_service(cwd, service_module, run_daemon, run_ssl)
    return all_p


def start_service(cwd, service_module, run_daemon, run_ssl):
    """
    Starts SNET Daemon ("snetd") and the python module of the service
    at the passed gRPC port.
    """
    
    def add_extra_configs(conf):
        """Add Extra keys to snetd.config.json"""
        with open(conf, "r") as f:
            snetd_configs = json.load(f)
            if run_ssl:
                snetd_configs["ssl_cert"] = "/opt/singnet/.certs/fullchain.pem"
                snetd_configs["ssl_key"] = "/opt/singnet/.certs/privkey.pem"
                snetd_configs["payent_channel_ca_path"] = "/opt/singnet/.certs/ca.pem"
                snetd_configs["payent_channel_cert_path"] = "/opt/singnet/.certs/client.pem"
                snetd_configs["payent_channel_key_path"] = "/opt/singnet/.certs/client-key.pem"
                snetd_configs["payment_channel_ca_path"] = "/opt/singnet/.certs/ca.pem"
                snetd_configs["payment_channel_cert_path"] = "/opt/singnet/.certs/client.pem"
                snetd_configs["payment_channel_key_path"] = "/opt/singnet/.certs/client-key.pem"
            _network = "mainnet"
            if "ropsten" in conf:
                _network = "ropsten"
            infura_key = os.environ.get("INFURA_API_KEY", "")
            if infura_key:
                snetd_configs["ethereum_json_rpc_endpoint"] = "https://{}.infura.io/{}".format(_network, infura_key)
            snetd_configs["metering_end_point"] = "https://{}-marketplace.singularitynet.io/metering".format(_network)
            snetd_configs["free_call_signer_address"] = "0x3Bb9b2499c283cec176e7C707Ecb495B7a961ebf"
            snetd_configs["pvt_key_for_metering"] = os.environ.get("PVT_KEY_FOR_METERING", "")
        with open(conf, "w") as f:
            json.dump(snetd_configs, f, sort_keys=True, indent=4)
    
    all_p = []
    if run_daemon:
        for idx, config_file in enumerate(glob.glob("./snetd_configs/*.json")):
            add_extra_configs(config_file)
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


def kill_and_exit(all_p):
    for p in all_p:
        try:
            os.kill(p.pid, signal.SIGTERM)
        except Exception as e:
            log.error(e)
    exit(1)


if __name__ == "__main__":
    main()
