[issue-template]: ../../../../../issues/new?template=BUG_REPORT.md
[feature-template]: ../../../../../issues/new?template=FEATURE_REQUEST.md

![singnetlogo](../../docs/assets/singnet-logo.jpg 'SingularityNET')

# Sequence to Sequence - Video to Text

This service uses [S2VT](https://vsubhashini.github.io/s2vt.html) to describe video content with natural language text.

It is part of our third party [DNN Model Services](https://github.com/singnet/dnn-model-services).

## Getting Started

### Requirements

- [Python 2.7](https://www.python.org/downloads/release/python-2715/)
- [SNET CLI](https://github.com/singnet/snet-cli)

### Development

We recommend that you follow the setup from author's repository:
https://github.com/vsubhashini/caffe/tree/recurrent/examples/s2vt

You'll need the python Caffe module:
- You can run a Docker Container from [bvlc/caffe](https://hub.docker.com/r/bvlc/caffe/):

```
$ nvidia-docker run --name "SNET_VideoCaptioning" -p 7004:7004 -ti bvlc/caffe:gpu bash
```
- Inside the container install `python-tk` and `nano`:

```
# apt update
# apt install python-tk nano
```

Then clone this repository:

```
# git clone https://github.com/singnet/dnn-model-services.git
# cd dnn-model-services/services/s2vt-video-captioning
```

Necessary files:
- You can copy all files from author's repository setup and put them inside `service/utils/data`.
- Or, you can use the script `service/utils/get_s2vt.sh` to download them.
- You'll need the following files at `service/utils/data`:
  
```
# ls -la service/utils/data
total 882120
-rw-r--r-- 1 user user 553432081 Nov  6 10:59 VGG_ILSVRC_16_layers.caffemodel
-rwxr-xr-x 1 user user      2728 Nov  6 11:05 s2vt.words_to_preds.deploy.prototxt
-rw-r--r-- 1 user user 349436137 Nov  6 11:01 s2vt_vgg_rgb.caffemodel
-rw-r--r-- 1 user user      4582 Nov  6 11:03 vgg_orig_16layer.deploy.prototxt
-rw-r--r-- 1 user user    393710 Nov  6 10:59 yt_coco_mvad_mpiimd_vocabulary.txt
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
   "DAEMON_END_POINT": "0.0.0.0:7056",
   "IPFS_END_POINT": "http://ipfs.singularitynet.io:80",
   "BLOCKCHAIN_NETWORK_SELECTED": "ropsten",
   "PASSTHROUGH_ENABLED": true,
   "PASSTHROUGH_ENDPOINT": "http://localhost:7003",
   "ORGANIZATION_ID": "snet",
   "SERVICE_ID": "s2vt-video-captioning",
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
$ pip2 install -r requirements.txt
```
Generate the gRPC codes:
```
$ sh buildproto.sh
```
Start the service and `SNET Daemon`:
```
$ python2 run_video_cap_service.py
```

### Calling the service:

Inputs:
  - `url`: An YouTube video URL.
  - `start_time_sec`: Start time position, in seconds.
  - `stop_time_sec`: Stop time position, in seconds.
  - The time interval (stop-start) must be <= 20 seconds.

Local (testing purpose):

```
$ python2 test_call_video_cap_service.py 
Endpoint (localhost:7003): 
Method (video_cap): 
Url: http://crcv.ucf.edu/THUMOS14/UCF101/UCF101/v_PlayingGuitar_g05_c01.avi
StartTime(s): 0
StopTime (s): 0
{'Caption': '1\n00:00:00,00 --> 00:00:10,00\nA man is playing guitar.'}
```

Through SingularityNET (follow this [link](https://dev.singularitynet.io/tutorials/publish/) to learn how to publish a service and open a payment channel to be able to call it):

Assuming that you have an open channel to this service:

```
$ snet client call snet s2vt-video-captioning default_group video_cap '{"url": "http://crcv.ucf.edu/THUMOS14/UCF101/UCF101/v_PlayingGuitar_g05_c01.avi", "start_time_sec": "0", "stop_time_sec": "0"}'
...
Read call params from cmdline...

Calling service...

    response:
        value: '{''Caption'': ''1\n00:00:00,00 --> 00:00:10,00\nA man is playing guitar.''}'
```

## Contributing and Reporting Issues

Please read our [guidelines](https://dev.singularitynet.io/docs/contribute/contribution-guidelines/#submitting-an-issue) before submitting an issue. If your issue is a bug, please use the bug template pre-populated [here][issue-template]. For feature requests and queries you can use [this template][feature-template].

## Authors

* **Artur Gontijo** - *Maintainer* - [SingularityNET](https://www.singularitynet.io)
