[issue-template]: ../../../../../../issues/new?template=BUG_REPORT.md
[feature-template]: ../../../../../../issues/new?template=FEATURE_REQUEST.md

![singnetlogo](../../../../docs/assets/singnet-logo.jpg?raw=true 'SingularityNET')

# Object Detection and Image Recognition

This service uses 2 other services:
  - `yolov3-object-detection` [[Reference](https://pjreddie.com/darknet/yolo/)] to detect objects on images and;
  - `cntk-image-recon` [[Reference](https://cntk.ai/pythondocs/CNTK_301_Image_Recognition_with_Deep_Transfer_Learning.html)] to classify these objects.

It is part of our third party [DNN Model Services](https://github.com/singnet/dnn-model-services).

## Getting Started

### Requirements

- [Python 3.6.5](https://www.python.org/downloads/release/python-365/)
- [Node 8+ w/npm](https://nodejs.org/en/download/)

### Development

Clone this repository:
```
$ git clone https://github.com/singnet/dnn-model-services.git
$ cd dnn-model-services/Services/gRPC/meta-services/object-detection-image-recon
```

### Running the service:

To get the `ORGANIZATION_NAME` and `SERVICE_NAME` you must have already published a service (check this [link](https://github.com/singnet/wiki/tree/master/tutorials/howToPublishService)).

Create the `SNET Daemon`'s config JSON file (`snetd.config.json`).

```
{
   "DAEMON_END_POINT": "DAEMON_HOST:DAEMON_PORT",
   "ETHEREUM_JSON_RPC_ENDPOINT": "https://kovan.infura.io",
   "IPFS_END_POINT": "http://ipfs.singularitynet.io:80",
   "REGISTRY_ADDRESS_KEY": "0x2e4b2f2b72402b9b2d6a7851e37c856c329afe38",
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
   "DAEMON_END_POINT": "http://54.203.198.53:7006",
   "ETHEREUM_JSON_RPC_ENDPOINT": "https://kovan.infura.io",
   "IPFS_END_POINT": "http://ipfs.singularitynet.io:80",
   "REGISTRY_ADDRESS_KEY": "0x2e4b2f2b72402b9b2d6a7851e37c856c329afe38",
   "PASSTHROUGH_ENABLED": true,
   "PASSTHROUGH_ENDPOINT": "http://localhost:7003",
   "ORGANIZATION_NAME": "snet",
   "SERVICE_NAME": "object-detection-image-recon",
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
$ python3 run_ObjectDetection_ImageRecon_service.py
```

### Calling the service:

Inputs:
  - `model_detect`: DNN Model ("yolov3").
  - `model_recon`: DNN Model ("ResNet152").
  - `img_path`: An image URL.
  - `confidence`: Confidence of object detection (between 0 and 1).

Local (testing purpose):

```
$ python3 test_ObjectDetection_ImageRecon_service.py 
Endpoint (localhost:7003): <ENTER>
Model ImageRecon (ResNet152): <ENTER>
Confidence (0.7): <ENTER>
Image (Path or Link): https://www.mediastorehouse.com/p/172/dog-man-child-walking-labrador-lead-10489821.jpg
delta_time: "203.43261623382568"
boxes: "[[315.0, 76.0, 156, 310], [246.0, -1.5, 142, 381], [178.0, 220.5, 114, 161]]"
confidences: "[0.9993983507156372, 0.9992683529853821, 0.9989995360374451]"
class_ids: "[0, 0, 16]"
top_1_list: "[\'56.95%: Canaan_dog\']"
```

Through SingularityNET (follow this [link](https://github.com/singnet/wiki/blob/master/tutorials/howToPublishService/README.md) to learn how to publish a service and open a payment channel to be able to call it):

Assuming that you have an open channel (`id: 0`) to this service:

```
$ snet client call 0 0.00000001 54.203.198.53:7006 detect_recon '{"model_detect": "yolov3", "model_recon": "ResNet152", "img_path": "https://figopetinsurance.com/sites/default/files/styles/blog_detail/public/imagedogsman-and-dog-hiking-mountainsblog.jpg", "confidence": "0.5"}'
...
Read call params from cmdline...

Calling service...

    response:
        boxes: '[[340.5, 113.5, 153, 361], [432.5, 162.5, 73, 119], [256.5, 219.0, 133, 278]]'
        class_ids: '[0, 24, 16]'
        confidences: '[0.9899819493293762, 0.971903383731842, 0.9540891647338867]'
        delta_time: '202.7593548297882'
        top_1_list: '[''78.86%: Australian_cattle_dog'']'
```

## Contributing and Reporting Issues

Please read our [guidelines](https://github.com/singnet/wiki/blob/master/guidelines/CONTRIBUTING.md#submitting-an-issue) before submitting an issue. If your issue is a bug, please use the bug template pre-populated [here][issue-template]. For feature requests and queries you can use [this template][feature-template].

## Authors

* **Artur Gontijo** - *Maintainer* - [SingularityNET](https://www.singularitynet.io)
