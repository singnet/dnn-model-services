[issue-template]: ../../../../../issues/new?template=BUG_REPORT.md
[feature-template]: ../../../../../issues/new?template=FEATURE_REQUEST.md

![singnetlogo](../../docs/assets/singnet-logo.jpg 'SingularityNET')

# Sound Spleeter

This service uses [Spleeter](https://github.com/deezer/spleeter) to perform source separation on audio files.

It is part of our third party [DNN Model Services](https://github.com/singnet/dnn-model-services).

## Getting Started

### Requirements

- [Python 3.6.5](https://www.python.org/downloads/release/python-365/)
- [SNET CLI](https://github.com/singnet/snet-cli)

### Development

Clone this repository:

```
$ git clone https://github.com/singnet/dnn-model-services.git
$ cd dnn-model-services/services/sound-spleeter
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
   "SERVICE_ID": "sound-spleeter",
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
$ python3 run_sound_spleeter_service.py
```

### Calling the service:

Inputs:
  - `url`: An audio file URL.

Local (testing purpose):

```
$ python3 test_sound_spleeter_service.py
Endpoint (localhost:7003):
Audio (URL): http://54.203.198.53:7000/Resources/audio_example.mp3
{'vocals': '...', 'accomp': '...'}
```

Through SingularityNET (follow this [link](https://dev.singularitynet.io/tutorials/publish/) to learn how to publish a service and open a payment channel to be able to call it):

Assuming that you have an open channel to this service:

```
$ snet client call snet sound-spleeter default_group spleeter '{"audio_url": "http://54.203.198.53:7000/Resources/audio_example.mp3"}'
...
Read call params from cmdline...

Calling service...

    response:
        value: '{'vocals': '...', 'accomp': '...'}'
```

## Contributing and Reporting Issues

Please read our [guidelines](https://dev.singularitynet.io/docs/contribute/contribution-guidelines/#submitting-an-issue) before submitting an issue. If your issue is a bug, please use the bug template pre-populated [here][issue-template]. For feature requests and queries you can use [this template][feature-template].

## Authors

* **Artur Gontijo** - *Maintainer* - [SingularityNET](https://www.singularitynet.io)
