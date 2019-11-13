[issue-template]: ../../../issues/new?template=BUG_REPORT.md
[feature-template]: ../../../issues/new?template=FEATURE_REQUEST.md

![singnetlogo](../assets/singnet-logo.jpg?raw=true 'SingularityNET')

# I3D Video Action Recognition

This service uses [I3D](https://github.com/deepmind/kinetics-i3d) to perform action recognition on videos.

It is part of our third party [DNN Model Services](https://github.com/singnet/dnn-model-services).

### Welcome

The service receives a video and uses it as an input for a `I3D` models trained on Kinetics.

One model was trained, using Kinetics-400 and the other using Kinetics-600, to predict action on videos.

### What’s the point?

The service makes prediction using computer vision and machine learning techniques.

The service outputs a top 5 prediction list (ordered by confidence) based on the specified dataset (Kinetics 400 or 600).

### How does it work?

The user must provide the following inputs in order to start the service and get a response:

Inputs:
  - `model`: kinetics-i3d model ("400" or "600").
  - `url`: A video URL.

You can use this service from [SingularityNET DApp](http://beta.singularitynet.io/), clicking on `SNET/VideoActionRecognition`.

You can also call the service from SingularityNET CLI (`snet`).

Assuming that you have an open channel to this service:

```
$ snet client call snet i3d-video-action-recognition default_group video_action_recon '{"model": "400", "url": "http://crcv.ucf.edu/THUMOS14/UCF101/UCF101/v_CricketShot_g04_c02.avi"}'
...
Read call params from cmdline...

Calling service...

    response:
        value: '{'Action': 'playing cricket\t97.77%\nskateboarding\t0.71%\nrobot dancing\t0.56%\nroller skating\t0.56%\ngolf putting\t0.13%\n'}'
```

### What to expect from this service?

Input video:

![Guitar Splash 1](../assets/users_guide/playing_guitar.gif)

with:
- `model: 600`

Response:

```
playing guitar      99.66%
tapping guitar      0.22%
singing             0.07%
playing ukulele     0.03%
recording music     0.01%
```