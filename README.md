## Deep Neural Networks Model Services

 A collection of SingularityNET Services using third party DNN models.
___

#### Services Description:

- #### Images:

  - [CNTK_ImageRecon](Services/gRPC/CNTK_ImageRecon):
    - This service uses ResNet152 model, trained to recognize different types of flowers and dog breeds.
    - [Reference](https://cntk.ai/pythondocs/CNTK_301_Image_Recognition_with_Deep_Transfer_Learning.html)

  - [YOLOv3_ObjectDetection](Services/gRPC/YOLOv3_ObjectDetection):
    - This service uses YOLOv3 model to detect objects on images.
    - [Reference](https://pjreddie.com/darknet/yolo/)
    - ```
      @article{yolov3,
          title={YOLOv3: An Incremental Improvement},
          author={Redmon, Joseph and Farhadi, Ali},
          journal = {arXiv},
          year={2018}
      }
      ```

  - [Meta_Service](Services/gRPC/Meta_Services/ObjectDetection_ImageRecon):
    - This service uses two other services.
    First it calls `YOLOv3_ObjectDetection` and get all detected objects from an image.
    Then it calls `CNTK_ImageRecon` for each object and returns its classification.

- #### Videos:

  - [I3D_VideoActionRecognition](Services/gRPC/I3D_VideoActionRecognition):
    - This service uses I3D model to recognize actions on videos (with 400 or 600 labels).
    - [Reference](https://github.com/deepmind/kinetics-i3d)

  - [S2VT_VideoCaptioning](Services/gRPC/S2VT_VideoCaptioning):
    - This service uses "Sequence to Sequence - Video to Text" to describe video content with natural language text.
    - [Reference](https://vsubhashini.github.io/s2vt.html)
    - ```
      @inproceedings{venugopalan15iccv,
          title = {Sequence to Sequence -- Video to Text},
          author = {Venugopalan, Subhashini and Rohrbach, Marcus and Donahue, Jeff 
                    and Mooney, Raymond and Darrell, Trevor and Saenko, Kate},
          booktitle = {Proceedings of the IEEE International Conference on Computer Vision (ICCV)},
          year = {2015}
      }
      ```
