[issue-template]: ../../../../../issues/new?template=BUG_REPORT.md
[feature-template]: ../../../../../issues/new?template=FEATURE_REQUEST.md

![singnetlogo](../../docs/assets/singnet-logo.jpg 'SingularityNET')

# Scene Recognition

This service uses a ResNet18 convolutional neural network architecture trained on [Places365](http://places2.csail.mit.edu/download.html) to perform scene recognition on images.

It is part of our third party [DNN Model Services](https://github.com/singnet/dnn-model-services).

## Getting Started

### Requirements

- [Python 3.6.5](https://www.python.org/downloads/release/python-365/)
- [SNET CLI](https://github.com/singnet/snet-cli)
- ResNet pre-trained model and scene recognition attributes related files that are automatically downloaded by running the script for the first time.

### Development

Simply clone this repository and navigate to `places365-scene-recognition` service root directory:
```
$ git clone https://github.com/singnet/dnn-model-services.git
$ cd dnn-model-services/services/places365-scene-recognition
```

### Running the service:

To get the `ORGANIZATION_NAME` and `SERVICE_NAME` you must have already published this code as a SingularityNET service (check this [link](https://github.com/singnet/wiki/blob/master/tutorials/howToPublishService)).

Create `SNET Daemon`'s config JSON file (`snetd.config.json`).

```
{
   "DAEMON_END_POINT": "DAEMON_HOST:DAEMON_PORT",
   "IPFS_END_POINT": "http://ipfs.singularitynet.io:80",
   "BLOCKCHAIN_NETWORK_SELECTED": "BLOCKCHAIN_NETWORK",
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
In which:
- *DAEMON_END_POINT* is the endpoint at which your service's SNET Daemon awaits for client calls. If running from inside a Docker container, make sure to expose the port by using the `-p` flag on `docker run` (e.g. `docker run [...] -p HOST_PORT:CONTAINER_PORT [...]`);
- *BLOCKCHAIN_NETWORK_SELECTED* is the network. Should be `"ropsten"` for Ropsten Test Network to test your service;
- *IPFS_END_POINT* is the endpoint of IPFS instance to get service configuration metadata. Should be kept as `http://ipfs.singularitynet.io:80` for the current SNET's IPFS server;
- *PASSTHROUGH_ENABLED* should be kept as `true` so that the SNET Daemon forwards the data it receives to your service's endpoint. If set to `false` it will simply echo its inputs for testing purposes;
- *PASSTHROUGH_ENDPOINT* is the endpoint at which your service awaits for Daemon input. In this case we're using gRPC for Daemon-service communication so the service's endpoint should be a specific http host (`http://ip:port`). You're likely going to use `localhost` as you ip and specify a port;
- *ORGANIZATION_NAME* and *SERVICE_NAME* are the names of your organzation and service, respectively, under SingularityNET. [Click here](https://github.com/singnet/wiki/blob/master/tutorials/howToPublishService/README.md) to learn more about creating an organization and publishing a service;
- *LOG* specifies logging information.

For example:

```
$ cat snetd.config.json
{
   "DAEMON_END_POINT": "http://54.203.198.53:7019",
   "IPFS_END_POINT": "http://ipfs.singularitynet.io:80",
   "BLOCKCHAIN_NETWORK_SELECTED": "ropsten",
   "PASSTHROUGH_ENABLED": true,
   "PASSTHROUGH_ENDPOINT": "http://localhost:7018",
   "ORGANIZATION_NAME": "snet",
   "SERVICE_NAME": "places365-scene-recognition",
   "LOG": {
       "LEVEL": "debug",
       "OUTPUT": {
           "TYPE": "stdout"
           }
   }
}
```
Install all dependencies (make sure `pip` installs the packages for Python3.6):
```
$ pip install -r requirements.txt
```
Your service's protobuf file is used to encode all client calls to it to make sure such calls are correct (i.e. the request follows the pattern the service expects). Build the protobuf file to automatically generate python code for the gRPC classes:
```
$ sh buildproto.sh
```
Start the service and its respective instance of `SNET Daemon` at the ports specified above:
```
$ python3 run_object_detection_service.py
```

### Calling the service:
> Go to this service's [User's Guide](../../../docs/users_guide/places365-scene-recognition.md) to see example calls and its outputs. 

#### Inputs:
  - `input_image`:  The URL for an input `.jpg` or `.png` image.
  - `predict`: A word ot set of comma separated words that specify what you want the service to predict using `input_image`. If left empty, all possible predictions will be made. Possible values are:
    - "io": to predict whether its an indoor or outdoor scene;
    - "categories": to output the top-5 scene category predictions and its probabilities;
    - "attributes": to output a prediction of a series of adjectives related to the scene;
    - "cam": to output "class activation mappings", a _base64 encoded_ heatmap image that shows which regions of the input image were more relevant for the prediction.

#### Local Call (for testing purpose):

Run the test script provided. You can input the gRPC request fields manually or use the flag `auto` to automatically fill them in using default values.
```
$ python3 test_scene_recognition_service.py auto
...
TEST RESULT: 
io: outdoor
categories:  0.660 -> volleyball_court/outdoor, 0.102 -> beach, 0.085 -> beach_house, 0.027 -> lagoon, 0.021 -> promenade,
attributes: open area, natural light, sunny, far-away horizon, warm, man-made, clouds, sand, touring
CAM saved to ./test_cam.jpg
Service completed!
```

#### Through SingularityNET 
> Follow this [link](https://github.com/singnet/wiki/blob/master/tutorials/howToPublishService/README.md) to learn how to publish a service and open a payment channel to be able to call it.

Assuming that you have an open channel to this service, you need `0` AGI to call the service at its Daemon's endpoint (`54.203.198.53:7019`). The only call method available for this service is `recognize_scene`, which has been defined at its protobuf file. Specifying the URL to an `input_image` and telling the service what to `predict`, the full example call (and its outputs) would be:

```
$ snet client call snet places365-scene-recognition default_group recognize_scene '{"input_image":"https://static1.squarespace.com/static/564783d5e4b077901c4bdc37/t/5a823d47c83025d76ac6ddae/1518484818865/Piccolo-104.jpg?format=1500w", "predict":"io, categories"}'
...
data: "{\"io\": \"indoor\", \"categories\": \" 0.924 -> beauty_salon, 0.006 -> gymnasium/indoor, 0.005 -> clean_room, 0.005 -> biology_laboratory, 0.004 -> chemistry_lab,\"}"
```

## Contributing and Reporting Issues

Please read our [guidelines](https://github.com/singnet/wiki/blob/master/guidelines/CONTRIBUTING.md#submitting-an-issue) before submitting an issue. If your issue is a bug, please use the bug template pre-populated [here][issue-template]. For feature requests and queries you can use [this template][feature-template].

## Authors

* **Ramon Durães** - *Maintainer* - [SingularityNET](https://www.singularitynet.io)
