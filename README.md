## Deep Neural Networks Model Services

- ##### A collection of SingularityNET Services using DNN.
___

#### Services description:

- ##### Images:

  - `CNTK_ImageRecon`:  
    - [Reference](https://cntk.ai/pythondocs/CNTK_301_Image_Recognition_with_Deep_Transfer_Learning.html)
    - This service uses ResNet152 model trained to recognize different types of flowers and dog breeds.
  
  - `YOLOv3_ObjectDetection`:  
    - [Reference](https://pjreddie.com/darknet/yolo/)
    - This service uses YOLOv3 model to detect objects on images.
  
  - `Meta_Services`:  
    - This service uses two other services.
    First it calls `YOLOv3_ObjectDetection` and get all detected objects from an image.
    Then it calls `CNTK_ImageRecon` for each object and returns a classification for each one.

- ##### Videos:

  - `I3D_VideoActionRecognition`:  
    - [Reference](https://github.com/deepmind/kinetics-i3d)
    - This service uses I3D model to recognize actions on videos (with 400 or 600 labels).
  
  - `S2VT_VideoCaptioning`:  
    - [Reference](https://vsubhashini.github.io/s2vt.html)
    - This service uses "Sequence to Sequence - Video to Text" to describe video content with natural language text.
