[issue-template]: ../../../../../issues/new?template=BUG_REPORT.md
[feature-template]: ../../../../../issues/new?template=FEATURE_REQUEST.md

![singnetlogo](../../../docs/assets/singnet-logo.jpg?raw=true 'SingularityNET')

# CNTK Image Recognition

This service uses [CNTK Image Recognition](https://cntk.ai/pythondocs/CNTK_301_Image_Recognition_with_Deep_Transfer_Learning.html) to perform image recognition on photos.

It is part of our third party [DNN Model Services](https://github.com/singnet/dnn-model-services).

## Getting Started

### Requirements

- [Python 3.6.5](https://www.python.org/downloads/release/python-365/)
- [Node 8+ w/npm](https://nodejs.org/en/download/)
- Pre-trained models (dogs and flowers)

### Development

Clone this repository and download the models using the `get_cntk_models.sh` script:

```
$ git clone https://github.com/singnet/dnn-model-services.git
$ cd dnn-model-services/utils
$ ./get_cntk_models.sh
$ ls -la Resources/Models
total 458416
drwxrwxr-x 2 user user      4096 Nov  8 08:49 .
drwxrwxr-x 3 user user      4096 Nov  8 08:49 ..
-rw-rw-r-- 1 user user 234830033 Ago 28 17:28 dogs_ResNet152_20.model
-rw-rw-r-- 1 user user 234574954 Ago 28 15:57 flowers_ResNet152_20.model
$ cd ../Services/gRPC/cntk-image-recon
```

### Running the service:

To get the `ORGANIZATION_NAME` and `SERVICE_NAME` you must have already published a service (check this [link](https://github.com/singnet/wiki/tree/master/tutorials/howToPublishService)).

Create the `SNET Daemon`'s config JSON file (`snetd.config.json`).

```
{
   "DAEMON_END_POINT": "DAEMON_HOST:DAEMON_PORT",
   "ETHEREUM_JSON_RPC_ENDPOINT": "https://kovan.infura.io",
   "IPFS_END_POINT": "http://ipfs.singularitynet.io:80",
   "REGISTRY_ADDRESS_KEY": "0xe331bf20044a5b24c1a744abc90c1fd711d2c08d",
   "PASSTHROUGH_ENABLED": true,
   "PASSTHROUGH_ENDPOINT": "SERVICE_GRPC_HOST:SERVICE_GRPC_PORT",  
   "ORGANIZATION_NAME": "ORGANIZATION_NAME",
   "SERVICE_NAME": "SERVICE_NAME",
   "LOG": {
       "LEVEL": "debug",
       "OUTPUT": {
            "TYPE": "stdout"
           }
   }
}
```

For example:

```
$ cat snetd.config.json
{
   "DAEMON_END_POINT": "http://54.203.198.53:7004",
   "ETHEREUM_JSON_RPC_ENDPOINT": "https://kovan.infura.io",
   "IPFS_END_POINT": "http://ipfs.singularitynet.io:80",
   "REGISTRY_ADDRESS_KEY": "0xe331bf20044a5b24c1a744abc90c1fd711d2c08d",
   "PASSTHROUGH_ENABLED": true,
   "PASSTHROUGH_ENDPOINT": "http://localhost:7003",
   "ORGANIZATION_NAME": "snet",
   "SERVICE_NAME": "cntk-image-recon",
   "LOG": {
       "LEVEL": "debug",
       "OUTPUT": {
           "TYPE": "stdout"
           }
   }
}
```
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
$ python3 run_image_recon_service.py
```

### Calling the service:

Inputs:
  - `gRPC method`: flowers or dogs.
  - `model`: DNN Model ("ResNet152").
  - `img_path`: An image URL.

Local (testing purpose):

```
$ python3 test_image_recon_service.py 
Endpoint (localhost:7003): 
Method (flowers|dogs): flowers
Model (ResNet152): <ENTER>
Image (Link): https://www.fiftyflowers.com/site_files/FiftyFlowers/Image/Product/Mini-Black-Eye-bloom-350_c7d02e72.jpg
1.8751
{1: '98.93%: sunflower', 2: '00.64%: black-eyed susan', 3: '00.16%: barbeton daisy', 4: '00.14%: oxeye daisy', 5: '00.03%: daffodil'}

$ python3 test_image_recon_service.py 
Endpoint (localhost:7003): 
Method (flowers|dogs): dogs
Model (ResNet152): <ENTER>
Image (Link): https://cdn2-www.dogtime.com/assets/uploads/2011/01/file_22950_standard-schnauzer-460x290.jpg
1.5280
{1: '99.83%: Miniature_schnauzer', 2: '00.09%: Alaskan_malamute', 3: '00.05%: Giant_schnauzer', 4: '00.01%: Bouvier_des_flandres', 5: '00.01%: Lowchen'}
```

Through SingularityNET (follow this [link](https://github.com/singnet/wiki/blob/master/tutorials/howToPublishService/README.md) to learn how to publish a service and open a payment channel to be able to call it):

Assuming that you have an open channel (`id: 0`) to this service:

```
$ snet client call 0 0.00000001 54.203.198.53:7004 flowers '{"model": "ResNet152", "img_path": "https://www.fiftyflowers.com/site_files/FiftyFlowers/Image/Product/Mini-Black-Eye-bloom-350_c7d02e72.jpg"}'
...
Read call params from cmdline...

Calling service...

    response:
        delta_time: '1.5536'
        top_5: '{1: ''98.93%: sunflower'', 2: ''00.64%: black-eyed susan'', 3: ''00.16%:
            barbeton daisy'', 4: ''00.14%: oxeye daisy'', 5: ''00.03%: daffodil''}'
```

## Contributing and Reporting Issues

Please read our [guidelines](https://github.com/singnet/wiki/blob/master/guidelines/CONTRIBUTING.md#submitting-an-issue) before submitting an issue. If your issue is a bug, please use the bug template pre-populated [here][issue-template]. For feature requests and queries you can use [this template][feature-template].

## Authors

* **Artur Gontijo** - *Maintainer* - [SingularityNET](https://www.singularitynet.io)