[issue-template]: ../../../../../issues/new?template=BUG_REPORT.md
[feature-template]: ../../../../../issues/new?template=FEATURE_REQUEST.md

![singnetlogo](../../docs/assets/singnet-logo.jpg 'SingularityNET')

# I3D Video Action Recognition

This service uses [I3D](https://github.com/deepmind/kinetics-i3d) to perform action recognition on videos.

It is part of our third party [DNN Model Services](https://github.com/singnet/dnn-model-services).

## Getting Started

### Requirements

- [Python 3.6.5](https://www.python.org/downloads/release/python-365/)
- [SNET CLI](https://github.com/singnet/snet-cli)

### Development

Clone this repository:

```
$ git clone https://github.com/singnet/dnn-model-services.git
$ cd dnn-model-services/services/i3d-video-action-recognition
```

### Running the service:

To get the `ORGANIZATION_ID` and `SERVICE_ID` you must have already published a service (check this [link](https://dev.singularitynet.io/tutorials/publish/)).

Create the `SNET Daemon`'s config JSON file (`snetd.config.json`).

```
{
   "DAEMON_END_POINT": "DAEMON_HOST:DAEMON_PORT",
   "IPFS_END_POINT": "http://ipfs.singularitynet.io:80",
   "BLOCKCHAIN_NETWORK_SELECTED": "BLOCKCHAIN_NETWORK",
   "PASSTHROUGH_ENABLED": true,
   "PASSTHROUGH_ENDPOINT": "http://SERVICE_GRPC_HOST:SERVICE_GRPC_PORT",  
   "ORGANIZATION_ID": "ORGANIZATION_ID",
   "SERVICE_ID": "SERVICE_ID",
   "LOG": {
       "LEVEL": "debug",
       "OUTPUT": {
            "TYPE": "stdout"
           }
   }
}
```

For example (using the Ropsten testnet):

```
$ cat snetd.config.json
{
   "DAEMON_END_POINT": "0.0.0.0:7055",
   "IPFS_END_POINT": "http://ipfs.singularitynet.io:80",
   "BLOCKCHAIN_NETWORK_SELECTED": "ropsten",
   "PASSTHROUGH_ENABLED": true,
   "PASSTHROUGH_ENDPOINT": "http://localhost:7003",
   "ORGANIZATION_ID": "snet",
   "SERVICE_ID": "i3d-video-action-recognition",
   "LOG": {
       "LEVEL": "debug",
       "OUTPUT": {
           "TYPE": "stdout"
           }
   }
}
```

Note that we set `DAEMON_HOST = 0.0.0.0` because this service will run inside a Docker container.

Install all dependencies:
```
$ pip3 install -r requirements.txt
```
Generate the gRPC codes:
```
$ sh buildproto.sh
```
Start the service and `SNET Daemon`:
```
$ python3 run_video_action_recon_service.py
```

### Calling the service:

Inputs:
  - `model`: kinetics-i3d model ("400" or "600").
  - `url`: A video URL.

Local (testing purpose):

```
$ python3 test_call_video_action_recon_service.py
Endpoint (localhost:7003):
Method (video_action_recon): 
Model: 400
Url: http://crcv.ucf.edu/THUMOS14/UCF101/UCF101/v_MoppingFloor_g25_c01.avi
{'Action': 'mopping floor\t56.66%\ncleaning floor\t31.83%\nsweeping floor\t11.39%\nsanding floor\t0.02%\nshoveling snow\t0.01%\n'}

$ python3 test_call_video_action_recon_service.py 
Endpoint (localhost:7003): <ENTER>
Method (video_action_recon): <ENTER>
Model: 600
Url: http://crcv.ucf.edu/THUMOS14/UCF101/UCF101/v_MoppingFloor_g25_c01.avi
{'Action': 'mopping floor\t54.51%\nsweeping floor\t41.16%\ncurling (sport)\t4.13%\ngolf driving\t0.05%\nplaying ice hockey\t0.03%\n'}
```

Through SingularityNET (follow this [link](https://dev.singularitynet.io/tutorials/publish/) to learn how to publish a service and open a payment channel to be able to call it):

Assuming that you have an open channel to this service:

```
$ snet client call snet i3d-video-action-recognition default_group video_action_recon '{"model": "400", "url": "http://crcv.ucf.edu/THUMOS14/UCF101/UCF101/v_CricketShot_g04_c02.avi"}'
...
Read call params from cmdline...

Calling service...

    response:
        value: '{'Action': 'playing cricket\t97.77%\nskateboarding\t0.71%\nrobot dancing\t0.56%\nroller skating\t0.56%\ngolf putting\t0.13%\n'}'
```

## Contributing and Reporting Issues

Please read our [guidelines](https://dev.singularitynet.io/docs/contribute/contribution-guidelines/#submitting-an-issue) before submitting an issue. If your issue is a bug, please use the bug template pre-populated [here][issue-template]. For feature requests and queries you can use [this template][feature-template].

## Authors

* **Artur Gontijo** - *Maintainer* - [SingularityNET](https://www.singularitynet.io)
