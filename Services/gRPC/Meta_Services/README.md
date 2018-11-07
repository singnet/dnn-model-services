## Creating a Meta Service

### 1. Cloning this repository:
```
$ git clone https://github.com/singnet/dnn-model-services.git
$ cd dnn-model-services/Services/gRPC/Meta_Services/ObjectDetection_ImageRecon/
```

### 2. SNET-CLI: Installation (v0.1.5)
```
$ cd /opt/snet
$ apt install libusb-1.0-0-dev libudev1 libudev-dev
$ pip3.6 install --upgrade pip
$ pip3.6 install snet_cli
```

- **SNET-CLI: Create an Identity**

-	snet identity create [identity_name] [identity_type]
	 - `identity_name` name of your SingularityNET Identity
	 - `identity_type` type of Identity (rpc, mnemonic, key, ledger or trezor)
```
$ snet identity create MY_ID_NAME key
Private key: <PASTE YOUR PRIVATE_KEY HERE>

set identity_name MY_ID_NAME
```

- **SNET-CLI: Publishing the Service (of your Agent)**

-   Now it's time to publish the service on the network!

```
$ cd service/
$ ls -la
total 44
drwxrwxr-x 3 artur artur 4096 Set 18 08:23 .
drwxrwxr-x 5 artur artur 4096 Set 18 08:08 ..
-rw-rw-r-- 1 artur artur  793 Set 11 09:17 common.py
-rw-rw-r-- 1 artur artur  991 Set 10 10:10 image_utils.py
-rw-rw-r-- 1 artur artur 1589 Set 11 09:17 __init__.py
-rw-rw-r-- 1 artur artur 7275 Set 17 07:52 ObjectDetection_ImageRecon.py
-rw-rw-r-- 1 artur artur 3195 Set 18 08:08 ObjectDetection_ImageRecon_service.py
drwxrwxr-x 2 artur artur 4096 Set 18 07:47 service_spec
-rw-rw-r-- 1 artur artur 5384 Set 18 08:08 snet_control.py
```
-	snet service init
```	
snet service init
Please provide values to populate your service.json file

Choose a name for your service: (default: "service")
MetaService
Choose the path to your service's spec directory: (default: "service_spec/")

Choose an organization to register your service under: (default: "")
ORGANIZATION_NAME
Choose the path under which your Service registration will be created: (default: "")

Choose a price in AGI to call your service: (default: 0)
5
Endpoint to call the API for your service: (default: "")
http://54.203.198.53:7009
Input a list of tags for your service: (default: [])
Meta, multiple, service
Input a description for your service: (default: "")
A service that calls another services.
{
    "name": "MetaService",
    "service_spec": "service_spec/",
    "organization": "ORGANIZATION_NAME",
    "path": "",
    "price": 5,
    "endpoint": "http://your_endpoint_ip:7009",
    "tags": [
        "Meta",
        "multiple",
        "service"
    ],
    "metadata": {
        "description": "A service that calls another services."
    }
}

service.json file has been created!
```
-	snet service publish
```
$ snet service publish
Creating transaction to create agent contract...

    transaction:
    chainId: 42
    data: '...'
    from: '0xFF2a327ed1Ca40CE93F116C5d6646b56991c0ddE'
    gas: 1788459
    gasPrice: 1000000000
    nonce: 241
    to: '0x1fAa8ec70aFe4f5ce904dA935A6ddF5f3482eEDb'
    value: 0

Proceed? (y/n): y
Submitting transaction...

    event_summaries:
    -   args:
        agent: '0x1591F7ecB3C4Fb2E57a2679c30aC8D9b4EC65248'
    event: AgentCreated
    receipt_summary:
    blockHash: '0x378d58f4a18f3e4a7b828e67c87c0db8fe8427d68c65686f76d0868f6a2927c2'
    blockNumber: 8458369
    cumulativeGasUsed: 7059222
    gasUsed: 1788285
    transactionHash: '0xb232da6977c1e427c6148071cd78de3b64a7db59ab8a17af5b36aa8b78208058'

Adding contract address to service.json file...

Creating transaction to create service registration...

    transaction:
    chainId: 42
    data: '...'
    from: '0xFF2a327ed1Ca40CE93F116C5d6646b56991c0ddE'
    gas: 1025279
    gasPrice: 1000000000
    nonce: 242
    to: '0x440cF8424fcD7Fc2D2fF3a5668c919E93A3d2aAb'
    value: 0

Proceed? (y/n): y
Submitting transaction...

    event_summaries:
    -   args:
        orgName: 534e45545f424800000000000000000000000000000000000000000000000000
        orgNameIndexed: 534e45545f424800000000000000000000000000000000000000000000000000
        serviceName: '4261736963536572766963650000000000000000000000000000000000000000'
        serviceNameIndexed: '4261736963536572766963650000000000000000000000000000000000000000'
    event: ServiceCreated
    receipt_summary:
    blockHash: '0x9dcecddcaaf10f17a0f0f958a3ae94514427cf2a62db51065c7b929af27bc89e'
    blockNumber: 8458371
    cumulativeGasUsed: 1048919
    gasUsed: 1025279
    transactionHash: '0x0105eaa581334c22e6a6d8957d735fd059484b2b57b553b941364c106417d889'
```
- **SNET-CLI: List Services**

- 	List services from a specific Organization ('ORGANIZATION_NAME')
```
$ snet organization list-services ORGANIZATION_NAME

List of ORGANIZATION_NAME's Services:
- SERVICE_NAME_1
- SERVICE_NAME_2
- MetaService

```

### 8. SNET DAEMON: Running the service
-   Go to the root of your service's folders.
-   Create a json file `snetd_[SERVICE_NAME]_config.json`
-   Save it inside a `config/` folder.
-   Generate the gRPC python codes (`buildproto.sh`).
-   Access your service endpoint and start the Daemon.

```
$ cat config/snetd_ObjectDetection_ImageRecon_service_config.json
{
    "DAEMON_TYPE": "grpc",
    "DAEMON_LISTENING_PORT": "7009",
    "BLOCKCHAIN_ENABLED": true,
    "ETHEREUM_JSON_RPC_ENDPOINT": "https://kovan.infura.io",
    "AGENT_CONTRACT_ADDRESS": "YOUR_AGENT_ADDRESS",
    "SERVICE_TYPE": "grpc",
    "PASSTHROUGH_ENABLED": true,
    "PASSTHROUGH_ENDPOINT": "http://localhost:7008",
    "LOG_LEVEL": 10,
    "PRIVATE_KEY": "YOUR_PRIVATE_KEY"
}

$ sh buildproto.sh

$ python3.6 run_ObjectDetection_ImageRecon_service.py --daemon-conf config/
Launching service.ObjectDetection_ImageRecon_service on ports {'grpc': 7008, 'snetd': 7009}
2018-09-18 08:52:56,576 - [   DEBUG] - ObjectDetection_ImageRecon_service - DetectReconServicer created
DEBU[0000] starting daemon
```

### 9. Testing the Service (local)

-	On the same machine run the test script wile Daemon is running:
```
$ python3.6 test_ObjectDetection_ImageRecon_service.py 
Endpoint (localhost:7008): 
Model ImageRecon (ResNet152): 
Confidence (0.7): 0.1
Image (Path or Link): https://.../young-man-dog.jpg
delta_time: "202.44789671897888"
boxes: "[[98.0, 27.5, 280, 389], [227.5, 118.5, 197, 303]]"
confidences: "[0.9994020462036133, 0.9629678130149841]"
class_ids: "[0, 16]"
top_1_list: "[\'51.75%: German_shepherd_dog\']"
```
-   The service will first run the ObjectDetection and detect 2 bounding boxes.
-   Then it will run ImageRecon for these boxes (2 times)
-   The result is 2 objects detected (person[0] and dog[16]) and a classification `German_shepherd_dog` for the dog. 
