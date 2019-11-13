[issue-template]: ../../../../../issues/new?template=BUG_REPORT.md
[feature-template]: ../../../../../issues/new?template=FEATURE_REQUEST.md

![singnetlogo](../../docs/assets/singnet-logo.jpg 'SingularityNET')

# VGG19 Pneumonia Diagnosis

This service uses [VGG19](http://www.robots.ox.ac.uk/~vgg/research/very_deep/) 
to detect whether patients have pneumonia, both bacterial and viral, based on an X-ray image of their chest.

This service is based on Alishba Imran's [work](https://github.com/alishbaimran/Pneumonia-Diagnosis-CNN-Model).

It is part of our third party [DNN Model Services](https://github.com/singnet/dnn-model-services).

## Getting Started

### Requirements

- [Python 3.6.5](https://www.python.org/downloads/release/python-365/)
- [SNET CLI](https://github.com/singnet/snet-cli)
- Pre-trained VGG19 Pneumonia Model

### Development

Clone this repository and download the model using the `get_pneumonia_model.sh` script:

```
$ git clone https://github.com/singnet/dnn-model-services.git
$ cd dnn-model-services/utils
$ ./get_pneumonia_model.sh
$ ls -la Resources/Models
total 179M
drwxr-xr-x 5 root root 4.0K Jul 12 11:23 ./
drwxr-xr-x 1 root root 4.0K Jul 11 14:24 ../
-rw-r--r-- 1 root root 179M Jul 12 11:23 PneumoniaModel.h5
$ cd ../services/pneumonia-diagnosis
```

### Running the service:

To get the `ORGANIZATION_ID` and `SERVICE_ID` you must have already published a service (check this [link](https://dev.singularitynet.io/tutorials/publish/)).

Create the `SNET Daemon`'s config JSON file (`snetd.config.json`).

```
{
   "DAEMON_END_POINT": "DAEMON_HOST:DAEMON_PORT",
   "IPFS_END_POINT": "http://ipfs.singularitynet.io:80",
   "BLOCKCHAIN_NETWORK_SELECTED": "BLOCKCHAIN_NETWORK",
   "PASSTHROUGH_ENABLED": true,
   "PASSTHROUGH_ENDPOINT": "http://SERVICE_GRPC_HOST:SERVICE_GRPC_PORT",  
   "ORGANIZATION_ID": "ORGANIZATION_ID",
   "SERVICE_ID": "SERVICE_ID",
   "LOG": {
       "LEVEL": "debug",
       "OUTPUT": {
            "TYPE": "stdout"
           }
   }
}
```

For example (using the Ropsten testnet):

```
$ cat snetd.config.json
{
   "DAEMON_END_POINT": "0.0.0.0:7062",
   "IPFS_END_POINT": "http://ipfs.singularitynet.io:80",
   "BLOCKCHAIN_NETWORK_SELECTED": "ropsten",
   "PASSTHROUGH_ENABLED": true,
   "PASSTHROUGH_ENDPOINT": "http://localhost:7003",
   "ORGANIZATION_ID": "snet",
   "SERVICE_ID": "pneumonia-diagnosis",
   "LOG": {
       "LEVEL": "debug",
       "OUTPUT": {
           "TYPE": "stdout"
           }
   }
}
```

Note that we set `DAEMON_HOST = 0.0.0.0` because this service will run inside a Docker container.

Install all dependencies:
```
$ pip3 install -r requirements.txt
```
Generate the gRPC codes:
```
$ sh buildproto.sh
```
Start the service and `SNET Daemon`:
```
$ python3 run_pneumonia_diagnosis_service.py
```

### Calling the service:

Inputs:
  - `img_path`: An X-ray chest image URL.

Local (testing purpose):

```
$ python3 test_pneumonia_diagnosis_service.py 
Endpoint (localhost:7003): 
Method (check): 
Image (Link): https://snet-models.s3.amazonaws.com/bh/PneumoniaDiagnosis/diagnosis_normal_1.jpg

Normal


$ python3 test_pneumonia_diagnosis_service.py 
Endpoint (localhost:7003): 
Method (check): 
Image (Link): https://snet-models.s3.amazonaws.com/bh/PneumoniaDiagnosis/diagnosis_pneumonia.jpg

Pneumonia
```

Through SingularityNET (follow this [link](https://dev.singularitynet.io/tutorials/publish/) to learn how to publish a service and open a payment channel to be able to call it):

Assuming that you have an open channel to this service:

```
$ snet client call snet pneumonia-diagnosis default_group check '{"img_path": "https://snet-models.s3.amazonaws.com/bh/PneumoniaDiagnosis/diagnosis_normal_2.jpg"}'
Price for this call will be 0.00000001 AGI (use -y to remove this warning). Proceed? (y/n): y
output: "Normal"
```

## Contributing and Reporting Issues

Please read our [guidelines](https://dev.singularitynet.io/docs/contribute/contribution-guidelines/#submitting-an-issue) before submitting an issue. If your issue is a bug, please use the bug template pre-populated [here][issue-template]. For feature requests and queries you can use [this template][feature-template].

## Authors

* **Artur Gontijo** - *Maintainer* - [SingularityNET](https://www.singularitynet.io)