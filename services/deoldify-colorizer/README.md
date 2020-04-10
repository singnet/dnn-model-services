[issue-template]: ../../../../../issues/new?template=BUG_REPORT.md
[feature-template]: ../../../../../issues/new?template=FEATURE_REQUEST.md

![singnetlogo](../../docs/assets/singnet-logo.jpg 'SingularityNET')

# DeOldify

This service uses [DeOldify](https://github.com/jantic/DeOldify) to perform automatic image colorization.

It is part of our third party [DNN Model Services](https://github.com/singnet/dnn-model-services).

## Getting Started

### Requirements

- [Python 3.6.5](https://www.python.org/downloads/release/python-365/)
- [SNET CLI](https://github.com/singnet/snet-cli)
- Pre-trained model (`ColorizeArtistic_gen.pth`)

### Development

Clone this repository and download the models using the `get_colorize_model.sh` script:

```
$ git clone https://github.com/singnet/dnn-model-services.git
$ cd dnn-model-services/utils
$ ./get_colorize_model.sh
$ ls -la Resources/Models
total 249188
drwxrwxr-x 2 ci ci      4096 Mar 24 13:30 ./
drwxrwxr-x 5 ci ci      4096 Mar 24 13:29 ../
-rw-rw-r-- 1 ci ci 255144681 Mar 24 13:30 ColorizeArtistic_gen.pth
-rw-rw-r-- 1 ci ci      9210 Mar 24 13:30 watermark.png
$ cd ../services/deoldify-colorizer
```

### Running the service:

To get the `ORGANIZATION_ID` and `SERVICE_ID` you must have already published a service (check this [link](https://dev.singularitynet.io/tutorials/publish/)).

Create the `SNET Daemon`'s config JSON file (`snetd.config.json`).

```
{
   "DAEMON_END_POINT": "DAEMON_HOST:DAEMON_PORT",
   "IPFS_END_POINT": "http://ipfs.singularitynet.io:80",
   "BLOCKCHAIN_NETWORK_SELECTED": "BLOCKCHAIN_NETWORK",
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
   "DAEMON_END_POINT": "0.0.0.0:7085",
   "IPFS_END_POINT": "http://ipfs.singularitynet.io:80",
   "BLOCKCHAIN_NETWORK_SELECTED": "ropsten",
   "PASSTHROUGH_ENDPOINT": "http://localhost:7003",
   "ORGANIZATION_ID": "snet",
   "SERVICE_ID": "deoldify-colorizer",
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
$ python3 run_service.py
```

### Calling the service:

Inputs:
  - `gRPC method`: colorize.
  - `img_input`: An image URL.

Local (testing purpose):

```
$ python3 test_service.py 
Endpoint (localhost:7003): 
Method (colorize): colorize
Image (Link): https://snet-models.s3.amazonaws.com/bh/Colorize/jucelino.jpg
[Base64 Image]
```

Through SingularityNET (follow this [link](https://dev.singularitynet.io/tutorials/publish/) to learn how to publish a service and open a payment channel to be able to call it):

Assuming that you have an open channel to this service:

```
$ snet client call snet deoldify-colorizer default_group colorize '{"img_input": "https://snet-models.s3.amazonaws.com/bh/Colorize/carnaval.jpg"}'

[Base64 Image]

```

## Contributing and Reporting Issues

Please read our [guidelines](https://dev.singularitynet.io/docs/contribute/contribution-guidelines/#submitting-an-issue) before submitting an issue. If your issue is a bug, please use the bug template pre-populated [here][issue-template]. For feature requests and queries you can use [this template][feature-template].

## Authors

* **Artur Gontijo** - *Maintainer* - [SingularityNET](https://www.singularitynet.io)