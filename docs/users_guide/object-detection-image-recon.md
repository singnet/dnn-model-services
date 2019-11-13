[issue-template]: ../../../../issues/new?template=BUG_REPORT.md
[feature-template]: ../../../../issues/new?template=FEATURE_REQUEST.md

![singnetlogo](../assets/singnet-logo.jpg?raw=true 'SingularityNET')

# Object Detection and Image Recognition

This service uses 2 other services:
  - `yolov3-object-detection` [[Reference](https://pjreddie.com/darknet/yolo/)] to detect objects on images and;
  - `cntk-image-recon` [[Reference](https://cntk.ai/pythondocs/CNTK_301_Image_Recognition_with_Deep_Transfer_Learning.html)] to classify these objects.

It is part of our third party [DNN Model Services](https://github.com/singnet/dnn-model-services).

### Welcome

This service is called `MetaService` because it calls other services to deliver a composed response. 

### What’s the point?

First the service calls `yolov3-object-detection` service and gets all detected objects from an image.
Then it calls `cntk-image-recon` service for each object and returns its classification.

### How does it work?

The user must provide the following inputs in order to start the service and get a response:

Inputs:
  - `model_detect`: DNN Model ("yolov3").
  - `model_recon`: DNN Model ("ResNet152").
  - `img_path`: An image URL.
  - `confidence`: Confidence of object detection (between 0 and 1).

You can use this service from [SingularityNET DApp](http://beta.singularitynet.io/), clicking on `SNET/MetaService`.

You can also call the service from SingularityNET CLI (`snet`).

Assuming that you have an open channel  to this service:

```
$ snet client call snet object-detection-image-recon default_group detect_recon '{"model_detect": "yolov3", "model_recon": "ResNet152", "img_path": "https://figopetinsurance.com/sites/default/files/styles/blog_detail/public/imagedogsman-and-dog-hiking-mountainsblog.jpg", "confidence": "0.5"}'
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

### What to expect from this service?

Input Image:

![BackpackManDog Splash 1](../assets/users_guide/backpack_man_dog.jpg)

with:
- `model_detect: yolov3`
- `model_recon: ResNet152`
- `confidence: 0.5`

Response:

```
boxes           [[292.0, 143.0, 292, 278], [42.5, 60.0, 251, 346], [13.0, 129.5, 182, 203]]
confidences     [0.9982979893684387, 0.9968200922012329, 0.8117520809173584]
class_ids       [16, 0, 24]
top_1_list      ['80.91%: Australian_shepherd']
```

The service first got 3 bounding boxes (with a dog [`16`], a person [`0`] and a backpack [`24`]) 
using `yolov3-object-detection`.

Then it got the breed of the found dog (`Australian_shepherd`) using `cntk-image-recon`.
