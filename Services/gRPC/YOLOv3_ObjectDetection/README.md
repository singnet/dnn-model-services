## Object Detection

### 1. Reference:

- This service uses [YOLOv3](https://pjreddie.com/darknet/yolo/) to perform object detection on images.

### 2. Preparing the file structure:

- For this service you'll need to download 2 additional files:
  - `yolov3.weights`
  - `yolov3.cfg`
- Clone this repository:
```
$ git clone https://github.com/singnet/dnn-model-services.git
$ cd dnn-model-services/utils
$ ./get_yolov3.sh
$ ls -la Resources/Models
total 242420
drwxrwxr-x 2 user user      4096 Nov  8 08:51 .
drwxrwxr-x 3 user user      4096 Nov  8 08:51 ..
-rw-rw-r-- 1 user user    213558 Nov  8 08:47 yolov3.cfg
-rw-rw-r-- 1 user user 248007048 Mar 25  2018 yolov3.weights
$ cd ..
```

### 3. Running the service:

- Create the SNET Daemon's config JSON file. It must looks like this:
```
$ cd Services/gRPC/YOLOv3_ObjectDetection
$ cat snetd_object_detection_service_config.json
{
    "DAEMON_TYPE": "grpc",
    "DAEMON_LISTENING_PORT": "7003",
    "BLOCKCHAIN_ENABLED": true,
    "ETHEREUM_JSON_RPC_ENDPOINT": "https://kovan.infura.io",
    "AGENT_CONTRACT_ADDRESS": "YOUR_AGENT_ADDRESS",
    "SERVICE_TYPE": "grpc",
    "PASSTHROUGH_ENABLED": true,
    "PASSTHROUGH_ENDPOINT": "http://localhost:7003",
    "LOG_LEVEL": 10,
    "PRIVATE_KEY": "YOUR_PRIVATE_KEY"
}
```
- Install all dependencies:
```
$ pip3 install -r requirements.txt
```
- Generate the gRPC codes:
```
$ sh buildproto.sh
```
- Start the service and SNET Daemon:
```
$ python3 run_image_recon_service.py --daemon-conf .
```

### 4. Calling the service:

- Inputs:
  - `model`: DNN Model ("ResNet152").
  - `img_path`: An image URL.

- Local (testing purpose):

```
$ python3 test_image_recon_service.py 
Endpoint (localhost:7000): 
Method (flowers|dogs): flowers
Model (ResNet152): <ENTER>
Image (Link): https://www.fiftyflowers.com/site_files/FiftyFlowers/Image/Product/Mini-Black-Eye-bloom-350_c7d02e72.jpg
3.8751
{1: '98.93%: sunflower', 2: '00.64%: black-eyed susan', 3: '00.16%: barbeton daisy', 4: '00.14%: oxeye daisy', 5: '00.03%: daffodil'}

$ python3 test_image_recon_service.py 
Endpoint (localhost:7000): 
Method (flowers|dogs): dogs
Model (ResNet152): <ENTER>
Image (Link): https://cdn2-www.dogtime.com/assets/uploads/2011/01/file_22950_standard-schnauzer-460x290.jpg
1.5280
{1: '99.83%: Miniature_schnauzer', 2: '00.09%: Alaskan_malamute', 3: '00.05%: Giant_schnauzer', 4: '00.01%: Bouvier_des_flandres', 5: '00.01%: Lowchen'}
```

- Through Blockchain:

```
$ snet set current_agent_at YOUR_AGENT_ADDRESS
set current_agent_at YOUR_AGENT_ADDRESS

$ snet client call flowers '{"model": "ResNet152", "img_path": "https://www.fiftyflowers.com/site_files/FiftyFlowers/Image/Product/Mini-Black-Eye-bloom-350_c7d02e72.jpg"}'
...
Read call params from cmdline...

Calling service...

    response:
        delta_time: '1.5536'
        top_5: '{1: ''98.93%: sunflower'', 2: ''00.64%: black-eyed susan'', 3: ''00.16%:
            barbeton daisy'', 4: ''00.14%: oxeye daisy'', 5: ''00.03%: daffodil''}'
            ```