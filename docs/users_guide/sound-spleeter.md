[issue-template]: ../../../issues/new?template=BUG_REPORT.md
[feature-template]: ../../../issues/new?template=FEATURE_REQUEST.md

![singnetlogo](../assets/singnet-logo.jpg?raw=true 'SingularityNET')

# Sound Spleeter

This service uses [Spleeter](https://github.com/deezer/spleeter) to perform source separation on audio files.

It is part of our third party [DNN Model Services](https://github.com/singnet/dnn-model-services).

### Welcome

The service receives an audio sample as input for source separation pre-trained model.

### What’s the point?

The service separates the vocals and the accompaniment from the input audio sample using machine learning techniques.

The service outputs two audio files (gRPC bytes) with both separations.

### How does it work?

The user must provide the following inputs in order to start the service and get a response:

Inputs:
  - `audio_url` or `audio`: An URL with an audio file (mp3) or an audio bytes array.

You can use this service from [SingularityNET DApp](http://beta.singularitynet.io/), clicking on `SNET/SoundSpleeter`.

You can also call the service from SingularityNET CLI (`snet`).

Assuming that you have an open channel to this service:

```
$ snet client call --save-field vocals vocals.wav snet sound-spleeter default_group spleeter '{"audio_url": "http://54.203.198.53:7000/Resources/audio_example.mp3"}'
Price for this call will be 0.00000001 AGI (use -y to remove this warning). Proceed? (y/n): y
```

The WAV audio file will be saved in `vocals.wav`!

### What to expect from this service?

Inputs:

- `audio`: [Slow Motion Dream by Steven M Bryant](http://54.203.198.53:7000/Resources/audio_example.mp3)

Response:

- `audio bytes array`: [Vocals](http://54.203.198.53:7000/Resources/vocals.wav)
- `audio bytes array`: [Accompaniment](http://54.203.198.53:7000/Resources/accompaniment.wav)
