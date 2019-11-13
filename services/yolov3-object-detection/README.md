[issue-template]: ../../../../../issues/new?template=BUG_REPORT.md
[feature-template]: ../../../../../issues/new?template=FEATURE_REQUEST.md

![singnetlogo](../../docs/assets/singnet-logo.jpg 'SingularityNET')

# Object Detection

This service uses [YOLOv3](https://pjreddie.com/darknet/yolo/) to perform object detection on images.

It is part of our third party [DNN Model Services](https://github.com/singnet/dnn-model-services).

## Getting Started

### Requirements

- [Python 3.6.5](https://www.python.org/downloads/release/python-365/)
- [SNET CLI](https://github.com/singnet/snet-cli)
- YOLOv3 files: `yolov3.weights` and `yolov3.cfg`

### Development

Clone this repository and download the necessary files using the `get_yolov3.sh` script:
```
$ git clone https://github.com/singnet/dnn-model-services.git
$ cd dnn-model-services/utils
$ ./get_yolov3.sh
$ ls -la Resources/Models
total 242420
drwxrwxr-x 2 user user      4096 Nov  8 08:51 .
drwxrwxr-x 3 user user      4096 Nov  8 08:51 ..
-rw-rw-r-- 1 user user    213558 Nov  8 08:47 yolov3.cfg
-rw-rw-r-- 1 user user 248007048 Mar 25  2018 yolov3.weights
$ cd ../services/yolov3-object-detection
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
   "DAEMON_END_POINT": "0.0.0.0:7057",
   "IPFS_END_POINT": "http://ipfs.singularitynet.io:80",
   "BLOCKCHAIN_NETWORK_SELECTED": "ropsten",
   "PASSTHROUGH_ENABLED": true,
   "PASSTHROUGH_ENDPOINT": "http://localhost:7003",
   "ORGANIZATION_ID": "snet",
   "SERVICE_ID": "yolov3-object-detection",
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
$ python3 run_object_detection_service.py
```

### Calling the service:

Inputs:
  - `model`: DNN Model ("yolov3").
  - `img_path`: An image URL.
  - `confidence`: Confidence of object detection (between 0 and 1).

Local (testing purpose):

```
$ python3 test_object_detection_service.py 
Endpoint (localhost:7003): 
Confidence (0.7): 
Image (Link): http://www.reidsitaly.com/images/planning/sightseeing/calcio.jpg
delta_time: "2.4893"
boxes: "[[150.5, 7.0, 31, 30], [219.5, 65.0, 73, 182], [275.0, 60.0, 212, 198]]"
class_ids: "[32, 0, 0]"
confidences: "[0.9988894462585449, 0.9795901775360107, 0.9754813313484192]"
... (BASE64_BBOX_IMAGE)
```

Through SingularityNET (follow this [link](https://dev.singularitynet.io/tutorials/publish/) to learn how to publish a service and open a payment channel to be able to call it):

Assuming that you have an open channel to this service:

```
$ snet client call snet yolov3-object-detection default_group detect '{"model": "yolov3", "img_path": "https://hips.hearstapps.com/amv-prod-cad-assets.s3.amazonaws.com/images/media/51/2017-10best-lead-photo-672628-s-original.jpg", "confidence": "0.5"}'
...
Read call params from cmdline...

Calling service...

    response:
        boxes: '[[8.5, 151.0, 223, 118], [294.0, 138.0, 78, 48], [127.0, 185.5, 250, 209],
            [605.0, 152.5, 224, 115], [432.0, 129.5, 86, 55], [205.5, 129.0, 81, 38],
            [18.5, 127.0, 127, 40], [439.5, 187.5, 299, 225], [525.0, 132.0, 88, 34],
            [694.5, 126.0, 115, 40]]'
        class_ids: '[2, 2, 2, 2, 2, 2, 2, 2, 2, 2]'
        confidences: '[0.998349130153656, 0.9982008337974548, 0.9977825284004211, 0.995550811290741,
            0.9875208735466003, 0.980316698551178, 0.9753901362419128, 0.969804048538208,
            0.9632347226142883, 0.9579626321792603]'
        delta_time: '2.0124'
        img_base64: ... (BASE64_BBOX_IMAGE)
```

## Contributing and Reporting Issues

Please read our [guidelines](https://dev.singularitynet.io/docs/contribute/contribution-guidelines/#submitting-an-issue) before submitting an issue. If your issue is a bug, please use the bug template pre-populated [here][issue-template]. For feature requests and queries you can use [this template][feature-template].

## Authors

* **Artur Gontijo** - *Maintainer* - [SingularityNET](https://www.singularitynet.io)
