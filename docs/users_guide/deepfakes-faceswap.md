[issue-template]: ../../../issues/new?template=BUG_REPORT.md
[feature-template]: ../../../issues/new?template=FEATURE_REQUEST.md

![singnetlogo](../assets/singnet-logo.jpg?raw=true 'SingularityNET')

# Deepfakes Faceswap

This service uses [faceswap](https://github.com/deepfakes/faceswap) to perform face swapping on videos.

It is part of our third party [DNN Model Services](https://github.com/singnet/dnn-model-services).

### Welcome

The service receives 2 videos URL as an input to train the model.

It returns a link (with an UID that can be used to make future requests to keep training/improving the same model).

With this link, users can check the progress of their requests in a dashboard.

### What’s the point?

The service extracts frames from input videos (A and B) and use these frames to train a face swapping model.

With the trained model, the service converts the video A with a face from video B, generating a new video.

### How does it work?

The user must provide the following inputs in order to start the service and get a response:

Inputs:
  - `gRPC method`: faceswap.
  - `uid`: To keep training the same model (optional)
  - `video_a`: URL to Video A (30 FPS, max size 20Mb).
  - `video_b`: URL to Video B (30 FPS, max size 20Mb).
  - `model_url`: URL to a pre-trained model (max: 320Mb, optional).

Note: Each call will train the model with 3000 iterations.

You can use this service from [SingularityNET DApp](http://beta.singularitynet.io/).

You can also call the service from SingularityNET CLI (`snet`).

Assuming that you have an open channel to this service:

```
$ snet client call snet deepfakes-faceswap default_group faceswap '{"video_a": "http://snet-models.s3.amazonaws.com/bh/Deepfakes/ben.mp4", "video_b": "http://snet-models.s3.amazonaws.com/bh/Deepfakes/musk.mp4"}'
uid: "http://52.38.111.172:7006/dashboard?uid=c5b28d375b53e6107f05"
```

### What to expect from this service?

Input Video A:

![Video A](../assets/users_guide/ben.png)

Input Video B:

![Video B](../assets/users_guide/musk.png)

Response:

Model trained with 100 iterations:

![Video Faceswap](../assets/users_guide/faceswap_100.png)

Model trained with 3k iterations:

![Video Faceswap](../assets/users_guide/faceswap_3k.png)

Model trained with 200k iterations:

![Video Faceswap](../assets/users_guide/faceswap_200k.png)