[issue-template]: ../../../../../issues/new?template=BUG_REPORT.md
[feature-template]: ../../../../../issues/new?template=FEATURE_REQUEST.md

![singnetlogo](../../docs/assets/singnet-logo.jpg 'SingularityNET')

# Real Time Voice Cloning

This service uses [Real-Time-Voice-Cloning](https://github.com/CorentinJ/Real-Time-Voice-Cloning) to clone a voice from
a 5 seconds audio file to generate arbitrary speech in real-time

It is part of our third party [DNN Model Services](https://github.com/singnet/dnn-model-services).

## Getting Started

### Requirements

- [Python 3.6.5](https://www.python.org/downloads/release/python-365/)
- [SNET CLI](https://github.com/singnet/snet-cli)
- Pre-trained model

### Development

Clone this repository and download the models using the `get_voice_models.sh` script:

```
$ git clone https://github.com/singnet/dnn-model-services.git
$ cd dnn-model-services/utils
$ ./get_voice_models.sh
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
   "DAEMON_END_POINT": "0.0.0.0:7065",
   "IPFS_END_POINT": "http://ipfs.singularitynet.io:80",
   "BLOCKCHAIN_NETWORK_SELECTED": "ropsten",
   "PASSTHROUGH_ENABLED": true,
   "PASSTHROUGH_ENDPOINT": "http://localhost:7003",
   "ORGANIZATION_ID": "snet",
   "SERVICE_ID": "real-time-voice-cloning",
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
$ python3 run_voice_cloning_service.py
```

### Calling the service:

Inputs:
  - `audio_url` or `audio`: An URL with an audio file (mp3 or wav) or an audio bytes array.
  - `sentence`: An english sentence in plain text (~20 words).

Local (testing purpose):

```
$ python3 test_voice_cloning_service.py 
Endpoint (localhost:7003): 
Audio (link): https://raw.githubusercontent.com/singnet/dnn-model-services/master/docs/assets/users_guide/ben_websumit19.mp3
Sentence (~20 words): I am an artificial intelligence researcher and I would like to make the world a better place!
{'audio': '...' }
```

Through SingularityNET (follow this [link](https://dev.singularitynet.io/tutorials/publish/) to learn how to publish a service and open a payment channel to be able to call it):

Assuming that you have an open channel to this service:

```
$ snet client call --save-field audio output.wav snet real-time-voice-cloning default_group clone '{"audio_url": "https://raw.githubusercontent.com/singnet/dnn-model-services/master/docs/assets/users_guide/ben_websumit19.mp3", "sentence": "I am an artificial intelligence researcher and I would like to make the world a better place!"}'
Price for this call will be 0.00000001 AGI (use -y to remove this warning). Proceed? (y/n): y
```

The WAV audio file will be saved in `output.wav`!

## Contributing and Reporting Issues

Please read our [guidelines](https://dev.singularitynet.io/docs/contribute/contribution-guidelines/#submitting-an-issue) before submitting an issue. If your issue is a bug, please use the bug template pre-populated [here][issue-template]. For feature requests and queries you can use [this template][feature-template].

## Authors

* **Artur Gontijo** - *Maintainer* - [SingularityNET](https://www.singularitynet.io)