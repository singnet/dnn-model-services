[issue-template]: ../../../issues/new?template=BUG_REPORT.md
[feature-template]: ../../../issues/new?template=FEATURE_REQUEST.md

![singnetlogo](../assets/singnet-logo.jpg?raw=true 'SingularityNET')

# Places365 Scene Recognition

> This is the user's guide to the "Places365 Scene Recognition Service". It is registered at Kovan Test Network onto SingularityNET's official organization (`snet`) under the name `places365-scene-recognition` as part of our third party [DNN Model Services](https://github.com/singnet/dnn-model-services).

### Welcome

This service uses a ResNet convolutional neural network model pre-trained on the [Places365](http://places2.csail.mit.edu/download.html) dataset to perform scene recognition and related tasks on images. 

### What’s the point?

Use this service to predict scene-related properties according to which flags to use as inputs, such as:
- whether its an indoor or outdoor environment (using the `io` flag); 
- what are the top-5 predictions of the scene where the photo was taken and its respective probabilities (`categories` flag);
- what are some scene related attributes (`attributes` flag);
- and even what regions of the image were the most relevant for the predictions, in which case you'd be shown what is called a "__c__lass __a__ctivation __m__apping": a heatmap image that highlights such high-relevance regions (`cam` flag).

### How does it work?

The service takes as inputs:
- `input_image`: the URL for a `.jpg` or `.png` input image over which the predictions will be made. This is a required field.
- `predict`: a string of comma-separated words describing what you want the service to return. Possible values are `io`, `categories`, `attributes` and `cam`. If left empty, it will return all possible predictions. See some example calls below.
And returns:
- a json-encoded string in which the keys are the words you use as inputs in the `predict` field and the values are their respective returns as strings. In the case of the class activation mappings (`cam`), it will be a base64-encoded `.jpg` image.

You can call the `places365-scene-recognition` service by installing the [SingularityNET Cli](https://github.com/snet-cli) through its `snet client call` command. Assuming you have an open channel to this service:

1. Use its CHANNEL_ID (e.g.: `270`); 
2. Specify a price in AGIs (e.g.: `0`, since its a free service);
3. Point to the endpoint at which this service's [SNET Daemon](https://github.com/singnet/snet-daemon) listens to the blockchain waiting for client calls: `54.203.198.53:7019`. You can obtain this and other information about registered services by running `snet service print_metadata ORGANIZATION SERVICE_NAME`.
4. Filling in some input data.

Example call:
```
$ snet client call 270 0 54.203.198.53:7019 recognize_scene '{"input_image":"https://static1.squarespace.com/static/564783d5e4b077901c4bdc37/t/5a823d47c83025d76ac6ddae/1518484818865/Piccolo-104.jpg?format=1500w", "predict":"io, categories"}'
...
data: "{\"io\": \"indoor\", \"categories\": \" 0.924 -> beauty_salon, 0.006 -> gymnasium/indoor, 0.005 -> clean_room, 0.005 -> biology_laboratory, 0.004 -> chemistry_lab,\"}"
```

_You'll soon also be able to call this service using a user interface through SingularityNET's DApp. Check [SNET's official website](http://singularitynet.io/) for updates._

### What to expect from this service?

Example 1:

- Input:

`input_image`: ![beach_input](../assets/users_guide/places365_example1_beach.png)
`predict`: "IO, Attributes, Categories, CAM"

- Output:

- `io`: 
- `categories`:
- `attributes`: 
- `cam`: ![beach_cam](../assets/users_guide/places365_example1_cam.jpg)

Example 2:

- Input:

- Output:

