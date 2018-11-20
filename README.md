[issue-template]: ../../issues/new?template=BUG_REPORT.md
[feature-template]: ../../issues/new?template=FEATURE_REQUEST.md

![singnetlogo](docs/assets/singnet-logo.jpg 'SingularityNET')

[![CircleCI](https://circleci.com/gh/arturgontijo/dnn-model-services.svg?style=svg)](https://circleci.com/gh/arturgontijo/dnn-model-services)

# Third Party Deep Neural Networks Model Services

A collection of services using third party DNN models.

## Getting Started

For more details on how to publish and test a service, select it from the list below:

### Images:
- [CNTK_ImageRecon](Services/gRPC/CNTK_ImageRecon) - This service uses ResNet152 model, trained to recognize different types of flowers and dog breeds. [[Reference](https://cntk.ai/pythondocs/CNTK_301_Image_Recognition_with_Deep_Transfer_Learning.html)]
- [YOLOv3_ObjectDetection](Services/gRPC/YOLOv3_ObjectDetection) - This service uses YOLOv3 model to detect objects on images. [[Reference](https://pjreddie.com/darknet/yolo/)]
    ```
      @article{yolov3,
          title={YOLOv3: An Incremental Improvement},
          author={Redmon, Joseph and Farhadi, Ali},
          journal = {arXiv},
          year={2018}
      }
    ```
- [Meta_Service](Services/gRPC/Meta_Services/ObjectDetection_ImageRecon) - This service uses two other services.
    First it calls `YOLOv3_ObjectDetection` and gets all detected objects from an image.
    Then it calls `CNTK_ImageRecon` for each object and returns its classification.

### Videos:
- [I3D_VideoActionRecognition](Services/gRPC/I3D_VideoActionRecognition) - This service uses I3D model to recognize actions on videos (with 400 or 600 labels). [[Reference](https://github.com/deepmind/kinetics-i3d)]
- [S2VT_VideoCaptioning](Services/gRPC/S2VT_VideoCaptioning) - This service uses "Sequence to Sequence - Video to Text" to describe video content with natural language text. [[Reference](https://vsubhashini.github.io/s2vt.html)]
    ```
      @inproceedings{venugopalan15iccv,
          title = {Sequence to Sequence -- Video to Text},
          author = {Venugopalan, Subhashini and Rohrbach, Marcus and Donahue, Jeff 
                    and Mooney, Raymond and Darrell, Trevor and Saenko, Kate},
          booktitle = {Proceedings of the IEEE International Conference on Computer Vision (ICCV)},
          year = {2015}
      }
    ```

### Contributing and Reporting Issues

Please read our [guidelines](https://github.com/singnet/wiki/tree/master/template/CONTRIBUTING.md#submitting-an-issue) before submitting an issue. If your issue is a bug, please use the bug template pre-populated [here][issue-template]. For feature requests and queries you can use [this template][feature-template].

## Authors

* **Artur Gontijo** - *Maintainer* - [SingularityNET](https://www.singularitynet.io)

## Licenses

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

Each service is licensed as followed:

- CNTK_ImageRecon - [MIT License](https://github.com/Microsoft/CNTK/blob/master/LICENSE.md)
- YOLOv3_ObjectDetection - [Public domain](https://github.com/pjreddie/darknet/blob/master/LICENSE)
- I3D_VideoActionRecognition - [Apache License 2.0](https://github.com/deepmind/kinetics-i3d/blob/master/LICENSE)
- S2VT_VideoCaptioning - [Attribution 4.0 International (CC BY 4.0)](http://creativecommons.org/licenses/by/4.0/)