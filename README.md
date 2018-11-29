[issue-template]: ../../issues/new?template=BUG_REPORT.md
[feature-template]: ../../issues/new?template=FEATURE_REQUEST.md

![singnetlogo](docs/assets/singnet-logo.jpg 'SingularityNET')

[![CircleCI](https://circleci.com/gh/singnet/dnn-model-services.svg?style=svg)](https://circleci.com/gh/singnet/dnn-model-services)

# Third Party Deep Neural Networks Model Services

A collection of services using third party DNN models.

[HTML User's Guide Hub](https://singnet.github.io/dnn-model-services/)


## Getting Started

For more details on how to publish and test a service, select it from the list below:

### Images:
- [cntk-image-recon](Services/gRPC/cntk-image-recon) ([User's Guide](docs/users_guide/cntk-image-recon.md)) - This service uses ResNet152 model, trained to recognize different types of flowers and dog breeds. [[Reference](https://cntk.ai/pythondocs/CNTK_301_Image_Recognition_with_Deep_Transfer_Learning.html)]
- [yolov3-object-detection](Services/gRPC/yolov3-object-detection) ([User's Guide](docs/users_guide/yolov3-object-detection.md)) - This service uses YOLOv3 model to detect objects on images. [[Reference](https://pjreddie.com/darknet/yolo/)]
    ```
      @article{yolov3,
          title={YOLOv3: An Incremental Improvement},
          author={Redmon, Joseph and Farhadi, Ali},
          journal = {arXiv},
          year={2018}
      }
    ```
- [meta-service-example](Services/gRPC/meta-services/object-detection-image-recon) ([User's Guide](docs/users_guide/object-detection-image-recon.md)) - This service uses two other services.
    First it calls `yolov3-object-detection` and gets all detected objects from an image.
    Then it calls `cntk-image-recon` for each object and returns its classification.

### Videos:
- [i3d-video-action-recognition](Services/gRPC/i3d-video-action-recognition) ([User's Guide](docs/users_guide/i3d-video-action-recognition.md)) - This service uses I3D model to recognize actions on videos (with 400 or 600 labels). [[Reference](https://github.com/deepmind/kinetics-i3d)]
- [s2vt-video-captioning](Services/gRPC/s2vt-video-captioning) ([User's Guide](docs/users_guide/s2vt-video-captioning.md)) - This service uses "Sequence to Sequence - Video to Text" to describe video content with natural language text. [[Reference](https://vsubhashini.github.io/s2vt.html)]
    ```
      @inproceedings{venugopalan15iccv,
          title = {Sequence to Sequence -- Video to Text},
          author = {Venugopalan, Subhashini and Rohrbach, Marcus and Donahue, Jeff 
                    and Mooney, Raymond and Darrell, Trevor and Saenko, Kate},
          booktitle = {Proceedings of the IEEE International Conference on Computer Vision (ICCV)},
          year = {2015}
      }
    ```

## Contributing and Reporting Issues

Please read our [guidelines](https://github.com/singnet/wiki/blob/master/guidelines/CONTRIBUTING.md#submitting-an-issue) before submitting an issue. If your issue is a bug, please use the bug template pre-populated [here][issue-template]. For feature requests and queries you can use [this template][feature-template].

## Authors

* **Artur Gontijo** - *Maintainer* - [SingularityNET](https://www.singularitynet.io)

## Licenses

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Each service is licensed as followed:

- cntk-image-recon - [MIT License](https://github.com/Microsoft/CNTK/blob/master/LICENSE.md)
- yolov3-object-detection - [Public domain](https://github.com/pjreddie/darknet/blob/master/LICENSE)
- i3d-video-action-recognition - [Apache License 2.0](https://github.com/deepmind/kinetics-i3d/blob/master/LICENSE)
- s2vt-video-captioning - [Attribution 4.0 International (CC BY 4.0)](http://creativecommons.org/licenses/by/4.0/)