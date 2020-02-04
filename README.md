[issue-template]: ../../issues/new?template=BUG_REPORT.md
[feature-template]: ../../issues/new?template=FEATURE_REQUEST.md

![singnetlogo](docs/assets/singnet-logo.jpg 'SingularityNET')

[![CircleCI](https://circleci.com/gh/singnet/dnn-model-services.svg?style=svg)](https://circleci.com/gh/singnet/dnn-model-services)

# Third Party Deep Neural Networks Model Services

A collection of services using third party DNN models.

[HTML User's Guide Hub](https://singnet.github.io/dnn-model-services/)


## Getting Started

For more details on how to publish and test a service, select it from the list below:

### Audio:
- [real-time-voice-cloning](services/real-time-voice-cloning) ([User's Guide](docs/users_guide/real-time-voice-cloning.md)) - This service uses Real-Time-Voice-Cloning to clone a voice from a 5 seconds audio file to generate arbitrary speech in real-time. [[Reference](https://github.com/CorentinJ/Real-Time-Voice-Cloning)]
- [sound-spleeter](services/sound-spleeter) ([User's Guide](docs/users_guide/sound-spleeter.md)) - This service uses Deezer's Spleeter to perform source separation on audio files. [[Reference](https://github.com/deezer/spleeter)]
    ```
     @misc{spleeter2019,
       title={Spleeter: A Fast And State-of-the Art Music Source Separation Tool With Pre-trained Models},
       author={Romain Hennequin and Anis Khlif and Felix Voituret and Manuel Moussallam},
       howpublished={Late-Breaking/Demo ISMIR 2019},
       month={November},
       note={Deezer Research},
       year={2019}
     }
    ```


### Images:
- [cntk-image-recon](services/cntk-image-recon) ([User's Guide](docs/users_guide/cntk-image-recon.md)) - This service uses ResNet152 model, trained to recognize different types of flowers and dog breeds. [[Reference](https://cntk.ai/pythondocs/CNTK_301_Image_Recognition_with_Deep_Transfer_Learning.html)]
- [deepfakes-faceswap](services/deepfakes-faceswap) ([User's Guide](docs/users_guide/deepfakes-faceswap.md)) - This service uses the Deepfakes Faceswap, trained on two input videos A and B, to perform face swapping on videos. [[Reference](https://github.com/deepfakes/faceswap)]
- [siggraph-colorization](services/siggraph-colorization) ([User's Guide](docs/users_guide/siggraph-colorization.md)) - This service learns to automatically color grayscale images with a deep network. [[Reference](http://iizuka.cs.tsukuba.ac.jp/projects/colorization/en/)]
    ```
     @Article{IizukaSIGGRAPH2016,
       author = {Satoshi Iizuka and Edgar Simo-Serra and Hiroshi Ishikawa},
       title = {{Let there be Color!: Joint End-to-end Learning of Global and Local Image Priors for Automatic Image Colorization with Simultaneous Classification}},
       journal = "ACM Transactions on Graphics (Proc. of SIGGRAPH 2016)",
       year = 2016,
       volume = 35,
       number = 4,
     }
    ```
- [yolov3-object-detection](services/yolov3-object-detection) ([User's Guide](docs/users_guide/yolov3-object-detection.md)) - This service uses YOLOv3 model to detect objects on images. [[Reference](https://pjreddie.com/darknet/yolo/)]
    ```
      @article{yolov3,
          title={YOLOv3: An Incremental Improvement},
          author={Redmon, Joseph and Farhadi, Ali},
          journal = {arXiv},
          year={2018}
      }
    ```
- [places365-scene-recognition](services/places365-scene-recognition) ([User's Guide](docs/users_guide/places365-scene-recognition.md)) - This service uses various convolutional neural networks trained on Places365 to perform scene recognition. [[Reference](https://github.com/CSAILVision/places365)]
    ```
      @article{zhou2017places,
           title={Places: A 10 million Image Database for Scene Recognition},
           author={Zhou, Bolei and Lapedriza, Agata and Khosla, Aditya and Oliva, Aude and Torralba, Antonio},
           journal={IEEE Transactions on Pattern Analysis and Machine Intelligence},
           year={2017},
           publisher={IEEE}
      }
    ```
- [pneumonia-diagnosis](services/pneumonia-diagnosis) ([User's Guide](docs/users_guide/pneumonia-diagnosis.md)) - This service uses VGG19 to classify X-ray chest images. Based on Alishba Imran's [work](https://github.com/alishbaimran/Pneumonia-Diagnosis-CNN-Model).

### Videos:
- [i3d-video-action-recognition](services/i3d-video-action-recognition) ([User's Guide](docs/users_guide/i3d-video-action-recognition.md)) - This service uses I3D model to recognize actions on videos (with 400 or 600 labels). [[Reference](https://github.com/deepmind/kinetics-i3d)]
- [s2vt-video-captioning](services/s2vt-video-captioning) ([User's Guide](docs/users_guide/s2vt-video-captioning.md)) - This service uses "Sequence to Sequence - Video to Text" to describe video content with natural language text. [[Reference](https://vsubhashini.github.io/s2vt.html)]
    ```
      @inproceedings{venugopalan15iccv,
          title = {Sequence to Sequence -- Video to Text},
          author = {Venugopalan, Subhashini and Rohrbach, Marcus and Donahue, Jeff 
                    and Mooney, Raymond and Darrell, Trevor and Saenko, Kate},
          booktitle = {Proceedings of the IEEE International Conference on Computer Vision (ICCV)},
          year = {2015}
      }
    ```

### Games:
- [zeta36-chess-alpha-zero](services/zeta36-chess-alpha-zero) ([User's Guide](docs/users_guide/zeta36-chess-alpha-zero.md)) - This service uses [AlphaGo Zero methods](https://deepmind.com/blog/alphago-zero-learning-scratch/)
 to learn and play chess. [[Reference](https://github.com/Zeta36/chess-alpha-zero)]

## Contributing and Reporting Issues

Please read our [guidelines](https://dev.singularitynet.io/docs/contribute/contribution-guidelines/#submitting-an-issue) before submitting an issue. If your issue is a bug, please use the bug template pre-populated [here][issue-template]. For feature requests and queries you can use [this template][feature-template].

## Authors

* **Artur Gontijo** - *Maintainer* - [SingularityNET](https://www.singularitynet.io)
* **Ramon Durães** - *Maintainer* - [SingularityNET](https://www.singularitynet.io)

## Licenses

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Each service is licensed as followed:


- cntk-image-recon - [MIT License](https://github.com/Microsoft/CNTK/blob/master/LICENSE.md)
- deepfakes-faceswap - [GPL-3.0](https://github.com/deepfakes/faceswap/blob/master/LICENSE)
- i3d-video-action-recognition - [Apache License 2.0](https://github.com/deepmind/kinetics-i3d/blob/master/LICENSE)
- places365-scene-recognition - [MIT License](https://github.com/CSAILVision/places365/blob/master/LICENSE)
- pneumonia-diagnosis - [Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/)
- real-time-voice-cloning - [MIT License](https://github.com/CorentinJ/Real-Time-Voice-Cloning/blob/master/LICENSE.txt)
- s2vt-video-captioning - [Attribution 4.0 International (CC BY 4.0)](http://creativecommons.org/licenses/by/4.0/)
- sound-spleeter - [MIT License](https://github.com/deezer/spleeter/blob/master/LICENSE)
- yolov3-object-detection - [Public domain](https://github.com/pjreddie/darknet/blob/master/LICENSE)
- zeta36-chess-alpha-zero - [MIT License](https://github.com/Zeta36/chess-alpha-zero/blob/master/LICENSE.txt)