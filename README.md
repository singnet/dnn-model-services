## Deep Neural Networks Model Services

 A collection of SingularityNET Services using third party DNN models.
___

#### Services Description:

- ##### Images:

  - `CNTK_ImageRecon`:
    - This service uses ResNet152 model, trained to recognize different types of flowers and dog breeds.
    - [Reference](https://cntk.ai/pythondocs/CNTK_301_Image_Recognition_with_Deep_Transfer_Learning.html)

  - `YOLOv3_ObjectDetection`:
    - This service uses YOLOv3 model to detect objects on images.
    - [Reference](https://pjreddie.com/darknet/yolo/)

  - `Meta_Services`:
    - This service uses two other services.
    First it calls `YOLOv3_ObjectDetection` and get all detected objects from an image.
    Then it calls `CNTK_ImageRecon` for each object and returns its classification.

- ##### Videos:

  - `I3D_VideoActionRecognition`:
    - This service uses I3D model to recognize actions on videos (with 400 or 600 labels).
    - [Reference](https://github.com/deepmind/kinetics-i3d)

  - `S2VT_VideoCaptioning`:
    - This service uses "Sequence to Sequence - Video to Text" to describe video content with natural language text.
    - [Reference](https://vsubhashini.github.io/s2vt.html)
