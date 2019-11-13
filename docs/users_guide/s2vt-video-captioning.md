[issue-template]: ../../../issues/new?template=BUG_REPORT.md
[feature-template]: ../../../issues/new?template=FEATURE_REQUEST.md

![singnetlogo](../assets/singnet-logo.jpg?raw=true 'SingularityNET')

# Sequence to Sequence - Video to Text

This service uses [S2VT](https://vsubhashini.github.io/s2vt.html) to describe video content with natural language text.

It is part of our third party [DNN Model Services](https://github.com/singnet/dnn-model-services).

### Welcome

The service receives a video and uses it as an input for a `VGG16` model that generates features of each frame.

Then all these frames are passed as input for a second model (`S2VT_VGG16`) that outputs a caption for all features.

### What’s the point?

The service makes prediction using computer vision and machine learning techniques.

The service outputs its best guess to describe an action on the specified time interval from 
a video (accordingly to confidence).

The output is delivered using `SRT` format.

### How does it work?

The user must provide the following inputs in order to start the service and get a response:

Inputs:
  - `url`: An YouTube video URL.
  - `start_time_sec`: Start time position, in seconds.
  - `stop_time_sec`: Stop time position, in seconds.
  - The time interval (stop-start) must be <= 20 seconds.

You can use this service from [SingularityNET DApp](http://beta.singularitynet.io/), clicking on `SNET/VideoCaptioning`.

You can also call the service from SingularityNET CLI (`snet`).

Assuming that you have an open channel to this service:

```
$ snet client call snet s2vt-video-captioning default_group video_cap '{"url": "http://crcv.ucf.edu/THUMOS14/UCF101/UCF101/v_PlayingGuitar_g05_c01.avi", "start_time_sec": "0", "stop_time_sec": "0"}'
...
Read call params from cmdline...

Calling service...

    response:
        value: '{''Caption'': ''1\n00:00:00,00 --> 00:00:10,00\nA man is playing guitar.''}'
```

### What to expect from this service?

Video Input:

![Drums Splash 1](../assets/users_guide/playing_drums.gif)

with:
- `start_time_sec: 0`
- `stop_time_sec: 0`

Response:
```
1
00:00:00,00 --> 00:00:12,00
A man is playing.
```