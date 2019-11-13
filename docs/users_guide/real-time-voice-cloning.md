[issue-template]: ../../../issues/new?template=BUG_REPORT.md
[feature-template]: ../../../issues/new?template=FEATURE_REQUEST.md

![singnetlogo](../assets/singnet-logo.jpg?raw=true 'SingularityNET')

# Real Time Voice Cloning

This service uses [Real-Time-Voice-Cloning](https://github.com/CorentinJ/Real-Time-Voice-Cloning) to clone a voice from 
5 seconds audio to generate arbitrary speech in real-time

It is part of our third party [DNN Model Services](https://github.com/singnet/dnn-model-services).

### Welcome

The service receives an audio sample and a sentence in plain english text.
It uses them as inputs for a pre-trained voice cloning models.

### What’s the point?

The service clones the voice from the input audio sample using machine learning techniques.

The service outputs an audio file (gRPC bytes) with the cloned voice speaking the input sentence.

### How does it work?

The user must provide the following inputs in order to start the service and get a response:

Inputs:
  - `audio_url` or `audio`: An URL with an audio file (mp3 or wav) or an audio bytes array.
  - `sentence`: An english sentence in plain text (~20 words).

You can use this service from [SingularityNET DApp](http://beta.singularitynet.io/), clicking on `SNET/RealTimeVoiceCloning`.

You can also call the service from SingularityNET CLI (`snet`).

Assuming that you have an open channel to this service:

```
$ snet client call --save-field audio output.wav snet real-time-voice-cloning default_group clone '{"audio_url": "https://raw.githubusercontent.com/singnet/dnn-model-services/master/docs/assets/users_guide/ben_websumit19.mp3", "sentence": "I am an artificial intelligence researcher and I would like to make the world a better place!"}'
Price for this call will be 0.00000001 AGI (use -y to remove this warning). Proceed? (y/n): y
```

The WAV audio file will be saved in `output.wav`!

### What to expect from this service?

Inputs:

- `audio`: [Ben Goertzel's Voice Sample](../assets/users_guide/ben_websumit19.mp3)
- `sentence`: "Given that most of the innovation in the AI algorithm and product worlds come from students, startups or independent developers."

Response:

- `audio bytes array`: [Voice Cloning Output](../assets/users_guide/ben_voice_cloning.mp3)
