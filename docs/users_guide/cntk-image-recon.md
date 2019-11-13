[issue-template]: ../../../issues/new?template=BUG_REPORT.md
[feature-template]: ../../../issues/new?template=FEATURE_REQUEST.md

![singnetlogo](../assets/singnet-logo.jpg?raw=true 'SingularityNET')

# CNTK Image Recognition

This service uses [CNTK Image Recognition](https://cntk.ai/pythondocs/CNTK_301_Image_Recognition_with_Deep_Transfer_Learning.html) to perform image recognition on photos.

It is part of our third party [DNN Model Services](https://github.com/singnet/dnn-model-services).

### Welcome

The service receives an image and uses it as an input for a pre-trained `ResNet152` model.

There are two pre-trained models available, one trained with a flowers dataset from the 
[Oxford Visual Geometry Group](http://www.robots.ox.ac.uk/~vgg/data/flowers/102/index.html), with 102 different categories of flowers common to the UK.

The second model was trained using the [Columbia Dogs Dataset](ftp://ftp.umiacs.umd.edu/pub/kanazawa/CU_Dogs.zip), with 133 different dog breeds.

### What’s the point?

The service makes prediction using computer vision and machine learning techniques.

The service outputs a top 5 prediction list (ordered by confidence) based on the specified dataset (flowers or dogs).

### How does it work?

The user must provide the following inputs in order to start the service and get a response:

Inputs:
  - `gRPC method`: flowers or dogs.
  - `model`: DNN Model ("ResNet152").
  - `img_path`: An image URL.

You can use this service from [SingularityNET DApp](http://beta.singularitynet.io/), clicking on `SNET/ImageRecon`.

You can also call the service from SingularityNET CLI (`snet`).

Assuming that you have an open channel to this service:

```
$ snet client call snet cntk-image-recon default_group flowers '{"model": "ResNet152", "img_path": "https://www.fiftyflowers.com/site_files/FiftyFlowers/Image/Product/Mini-Black-Eye-bloom-350_c7d02e72.jpg"}'
...
Read call params from cmdline...

Calling service...

    response:
        delta_time: '1.5536'
        top_5: '{1: ''98.93%: sunflower'', 2: ''00.64%: black-eyed susan'', 3: ''00.16%:
            barbeton daisy'', 4: ''00.14%: oxeye daisy'', 5: ''00.03%: daffodil''}'
```

### What to expect from this service?

Input image:

![Rose Splash 1](../assets/users_guide/rose.jpg)

Response:
```
1: '99.66%: rose'
2: '00.11%: mallow'
3: '00.04%: globe-flower'
4: '00.03%: bougainvillea'
5: '00.03%: anthurium'
```

Input image:

![Bulldog Splash 1](../assets/users_guide/bulldog.jpg)

Response:
```
1: '98.28%: Bulldog'
2: '00.54%: Bullmastiff'
3: '00.41%: American_staffordshire_terrier'
4: '00.16%: Chinese_shar-pei'
5: '00.12%: Dogue_de_bordeaux'
```