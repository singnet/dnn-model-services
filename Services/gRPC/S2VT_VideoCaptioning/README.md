## Sequence to Sequence - Video to Text

### 1. Reference:

- This service describes video content with natural language text based on [S2VT](https://vsubhashini.github.io/s2vt.html).

### 2. Setup from author's repository:

- We recommend you to follow the setup at author's repository:
https://github.com/vsubhashini/caffe/tree/recurrent/examples/s2vt
- You'll need the python Caffe module.
  - You can run a Docker Container from [bvlc/caffe](https://hub.docker.com/r/bvlc/caffe/):
  ```bash
  $ nvidia-docker run --name "SNET_VideoCaptioning" -p 7004:7004 -ti bvlc/caffe:gpu bash
  ```
  - Inside the container install `python-tk` and `nano`:
  ```
  # apt update
  # apt get install python-tk nano
  ```

### 3. Preparing the file structure:

- To get the `YOUR_AGENT_ADDRESS` you must have already published a service (check this [link](https://github.com/singnet/wiki/tree/master/tutorials/howToPublishService)).
- Then clone this repository:
```
$ git clone https://github.com/singnet/dnn-model-services.git
```

- Necessary files:
  - You can copy all files from setup (step 2) and put them inside `service/utils/data`
  - Or, you can use the script (`service/utils/get_s2vt.sh`) to download them.
  - You'll need the following files at `service/utils/data`:
  
```
$ cd dnn-model-services/Services/gRPC/S2VT_VideoCaptioning
$ ls -la service/utils/data
total 882120
-rw-r--r-- 1 user user 553432081 Nov  6 10:59 VGG_ILSVRC_16_layers.caffemodel
-rwxr-xr-x 1 user user      2728 Nov  6 11:05 s2vt.words_to_preds.deploy.prototxt
-rw-r--r-- 1 user user 349436137 Nov  6 11:01 s2vt_vgg_rgb.caffemodel
-rw-r--r-- 1 user user      4582 Nov  6 11:03 vgg_orig_16layer.deploy.prototxt
-rw-r--r-- 1 user user    393710 Nov  6 10:59 yt_coco_mvad_mpiimd_vocabulary.txt
```

### 4. Running the service:

- Create the SNET Daemon's config JSON file. It must looks like this:
```
$ cat snetd_video_cap_service_config.json
{
    "DAEMON_TYPE": "grpc",
    "DAEMON_LISTENING_PORT": "7004",
    "BLOCKCHAIN_ENABLED": true,
    "ETHEREUM_JSON_RPC_ENDPOINT": "https://kovan.infura.io",
    "AGENT_CONTRACT_ADDRESS": "YOUR_AGENT_ADDRESS",
    "SERVICE_TYPE": "grpc",
    "PASSTHROUGH_ENABLED": true,
    "PASSTHROUGH_ENDPOINT": "http://localhost:7003",
    "LOG_LEVEL": 10,
    "PRIVATE_KEY": "YOUR_PRIVATE_KEY"
}
```
- Install all dependencies (this service uses Python 2.7):
```
$ pip2 install -r requirements.txt
```
- Generate the gRPC codes:
```
$ sh buildproto.sh
```
- Start the service and SNET Daemon:
```
$ python2 run_video_cap_service.py --daemon-conf .
```

### 5. Calling the service:

- Inputs:
  - `url`: An YouTube video URL.
  - `start_time_sec`: Start time position, in seconds.
  - `stop_time_sec`: Stop time position, in seconds.
  - The delta time (stop-start) must be <= 20 seconds.

- Local (testing purpose):

```
$ python2 test_call_video_cap_service.py 
Endpoint (localhost:7003): <ENTER>
Method (video_cap): <ENTER>
Url: https://www.youtube.com/watch?v=WC5FdFlUcl0
StartTime(s): 96
StopTime (s): 101
{'Caption': '1\n00:01:36,00 --> 00:01:41,00\nA man is playing a song.'}
```

- Through SingularityNET:

```
$ snet set current_agent_at YOUR_AGENT_ADDRESS
set current_agent_at YOUR_AGENT_ADDRESS

$ snet client call video_cap '{"url": "https://www.youtube.com/watch?v=WC5FdFlUcl0", "start_time_sec": "96", "stop_time_sec": "101"}'
...
Read call params from cmdline...

Calling service...

    response:
        value: '{''Caption'': ''1\n00:01:36,00 --> 00:01:41,00\nA man is playing a song.''}'
```