## Getting Started with SNET DAEMON and SNET-CLI

### 1. Conect to the AWS machine.

### 2. List all images
```
$ docker images
nvidia/cuda    9.0-cudnn7-runtime-ubuntu16.04    4ee281bdc2ee    4 weeks ago    1.17GB
```

### 3. Start a container from Image ID ("4ee281bdc2ee")
```
$ docker run -ti 4ee281bdc2ee
```

### 4. Git: Installation
```
$ apt update
$ apt install -y git
```

### 5. SNET DAEMON: Installation
```
$ mkdir /opt/snet; cd /opt/snet
```

- **PYTHON 3.6: Installation**
```
	$ apt install -y build-essential checkinstall zlib1g-dev libreadline-gplv2-dev \
	libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev
	$ wget https://www.python.org/ftp/python/3.6.5/Python-3.6.5.tar.xz
	$ tar xvf Python-3.6.5.tar.xz
	$ cd Python-3.6.5/
	$ ./configure
	$ make -j8
	$ make altinstall
	$ cd..; rm -rf Python-3.6.5/; rm -f Python-3.6.5.tar.xz
```

- **NODEJS 8.x: Installation**
```
	$ curl -sL https://deb.nodesource.com/setup_8.x | sh
	$ apt install -y nodejs
	$ npm install -g npm
```

- **GO: Installation**
```
	$ apt install -y golang-1.10
	$ mkdir /opt/snet/go
	$ echo 'PS1="$PS1\n"' >> /root/.bashrc
	$ echo 'export GOPATH="/opt/snet/go"' >> /root/.bashrc
	$ echo 'export PATH="$PATH:/opt/snet/go/bin:/usr/lib/go-1.10/bin"' >> /root/.bashrc
	$ source /root/.bashrc
```

- **Go Extras: Installation**
```
	$ go get -v -u github.com/golang/dep/cmd/dep
	$ go get -v -u github.com/golang/protobuf/protoc-gen-go
	$ go get -v -u github.com/golang/lint/golint
```
- **Proto3: Installation**
```
	$ cd /opt/snet
	$ curl -OL https://github.com/google/protobuf/releases/download/v3.4.0/protoc-3.4.0-linux-x86_64.zip
	$ unzip protoc-3.4.0-linux-x86_64.zip -d protoc3
	$ mv protoc3/bin/* /usr/local/bin/
	$ mv protoc3/include/* /usr/local/include/
```
```
$ cd /opt/snet/go/src
$ git clone https://github.com/singnet/snet-daemon.git
$ cd snet-daemon
$ ./scripts/install
$ cp blockchain/agent.go vendor/github.com/singnet/snet-daemon/blockchain/
$ ./scripts/build linux amd64
$ cp build/snetd-linux-amd64 ../../bin/snetd
```

### 6. SNET DAEMON: Testing
```
$ snetd
DEBU[0000] error reading config        	...
ERRO[0000] Unable to initialize daemon 	...
```

### 7. SNET-CLI: Installation (v0.1.5)
```
$ cd /opt/snet
$ apt install libusb-1.0-0-dev libudev1 libudev-dev
$ pip3.6 install --upgrade pip
$ pip3.6 install snet_cli
```

### 8. Cloning this repository:
```
$ git clone https://github.com/singnet/dnn-model-services.git
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
$ cd dnn-model-services/Services/gRPC/Basic_Template/service/
```
-	snet service init
```	
$ snet service init
Please provide values to populate your service.json file

Choose a name for your service: (default: "BasicService")

Choose the path to your service's spec directory: (default: "service_spec/")

Choose an organization to register your service under: (default: "")
SNET_BH
Choose the path under which your Service registration will be created: (default: "")

Choose a price in AGI to call your service: (default: 0)
100
Endpoint to call the API for your service: (default: "")
http://54.203.198.53:7000
Input a list of tags for your service: (default: [])
Basic Service, Template, Arithmetic
Input a description for your service: (default: "")
A basic template to show how to publish a service on SingularityNET platform.
{
    "name": "BasicService",
    "service_spec": "service_spec/",
    "organization": "SNET_BH",
    "path": "",
    "price": 100,
    "endpoint": "http://54.203.198.53:7000",
    "tags": [
    "Basic",
    "Service,",
    "Template,",
    "Arithmetic"
    ],
    "metadata": {
    "description": "A basic template to show how to publish a service on SingularityNET platform."
    }
}

service.json file has been created!
```
-	Now you have to create the 'service_spec' folder and put the .proto file inside it.
```
$ mkdir service_spec
$ cp basic_tamplate_rpc.proto service_spec/
$ ls -la service_spec/
total 12
drwxrwxr-x 2 artur artur 4096 Ago 22 13:24 .
drwxrwxr-x 3 artur artur 4096 Ago 22 13:24 ..
-rw-rw-r-- 1 artur artur  375 Ago 22 13:18 basic_tamplate_rpc.proto
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

- 	List services from a specific Organization ('SNET_BH')
```
$ snet organization list-services SNET_BH

List of SNET_BH's Services:
- BasicService
```

- **SNET-CLI: Removing an Agent (Set your service unavailable)**

-	snet service delete [organization] [service_name]
	 - `organization` name of the Organization.
	 - `service_name` name of the Service.
```
$ snet service delete SNET_BH BasicService
Getting information about the service...
Deleting service BasicService...
Proceed? (y/n): y
Submitting transaction...

Removing current contract address from session...

unset current_agent_at

Service was deleted!
```
- **SNET-CLI: Checking you session**
```
$ snet session
    session:
    current_agent_at: 'YOUR_SERVICE_ADDRESS'
    default_eth_rpc_endpoint: https://kovan.infura.io
    default_gas_price: '1000000000'
    default_wallet_index: '0'
    identity_name: MY_ID_NAME
```
- **SNET-CLI: SET and UNSET**
-	If you need to change keys from your session.
```
	$ snet unset current_agent_at
	$ snet set current_agent_at 0x1591F7ecB3C4Fb2E57a2679c30aC8D9b4EC65248
```

### 8. SNET DAEMON: Running the service
-   Go to the root of your service's folders.
-   Create a json file `snetd_[SERVICE_NAME]_config.json`
-   Save it inside a `config/` folder.
-   Generate the gRPC python codes (`buildproto.sh`).
-   Access your service endpoint and start the Daemon.

```
$ cat config/snetd_basic_service_one_config.json
{
    "DAEMON_TYPE": "grpc",
    "DAEMON_LISTENING_PORT": "7000",
    "BLOCKCHAIN_ENABLED": true,
    "ETHEREUM_JSON_RPC_ENDPOINT": "https://kovan.infura.io",
    "AGENT_CONTRACT_ADDRESS": "YOUR_AGENT_ADDRESS",
    "SERVICE_TYPE": "grpc",
    "PASSTHROUGH_ENABLED": true,
    "PASSTHROUGH_ENDPOINT": "http://localhost:7003",
    "LOG_LEVEL": 10,
    "PRIVATE_KEY": "YOUR_PRIVATE_KEY"
}

$ sh buildproto.sh

$ python3.6 run_basic_service.py --daemon-config config/
Launching service.basic_service_one on ports {'grpc': 7003, 'snetd': 7000}
2018-08-22 16:48:48,343 - [   DEBUG] - basic_template - AdditionServicer created
2018-08-22 16:48:48,344 - [   DEBUG] - basic_template - SubtractionServicer created
2018-08-22 16:48:48,344 - [   DEBUG] - basic_template - MultiplicationServicer created
2018-08-22 16:48:48,344 - [   DEBUG] - basic_template - DivisionServicer created
DEBU[0000] starting daemon
```

### 9. SNET-CLI: Calling the Service (remote)

-	snet client call [method] '[json]'
	 - `method` one of your service's methods.
	 - `json` the params of the method.
```
	$ snet client call mul '{"a":12.0, "b":77.0}'
	set current_agent_at 0x1591F7ecB3C4Fb2E57a2679c30aC8D9b4EC65248

	Accept job price 0.00000100 AGI? (y/n): y
	Creating transaction to create job...

	    transaction:
		chainId: 42
		data: '0x5b6b5710'
		from: '0xFF2a327ed1Ca40CE93F116C5d6646b56991c0ddE'
		gas: 734276
		gasPrice: 1000000000
		nonce: 245
		to: '0x1591F7ecB3C4Fb2E57a2679c30aC8D9b4EC65248'
		value: 0

	Proceed? (y/n): y
	Submitting transaction...

	    event_summaries:
	    -   args:
		    consumer: '0xFF2a327ed1Ca40CE93F116C5d6646b56991c0ddE'
		    job: '0x5f8Db0C6F8c7757d2dd43611Ef024419e153Df67'
		    jobPrice: 100
		event: JobCreated
	    receipt_summary:
		blockHash: '0x5a6597b0588a895e56b1c66fa96b2e12900aa3c6018532ab887cfb327f1ccab5'
		blockNumber: 8458612
		cumulativeGasUsed: 1044692
		gasUsed: 734276
		transactionHash: '0xd5d07a7ad91fbd08539f358b4e573662aa9e7d0035ce13129dfbc19366cc7ac7'

	set current_job_at 0x5f8Db0C6F8c7757d2dd43611Ef024419e153Df67

	    jobs:
	    -   job_address: '0x5f8Db0C6F8c7757d2dd43611Ef024419e153Df67'
		job_price: 100

	set current_job_at 0x5f8Db0C6F8c7757d2dd43611Ef024419e153Df67

	Creating transaction to approve token transfer...

	    transaction:
		chainId: 42
		data: '...'
		from: '0xFF2a327ed1Ca40CE93F116C5d6646b56991c0ddE'
		gas: 45552
		gasPrice: 1000000000
		nonce: 246
		to: '0x3b226fF6AAd7851d3263e53Cb7688d13A07f6E81'
		value: 0

	Proceed? (y/n): y
	Submitting transaction...

	    event_summaries:
	    -   args:
		    owner: '0xFF2a327ed1Ca40CE93F116C5d6646b56991c0ddE'
		    spender: '0x5f8Db0C6F8c7757d2dd43611Ef024419e153Df67'
		    value: 100
		event: Approval
	    receipt_summary:
		blockHash: '0x97539ba13555d89132317fbee569c282d943b0b8f34052b37744dd403b4959a3'
		blockNumber: 8458613
		cumulativeGasUsed: 45552
		gasUsed: 45552
		transactionHash: '0x01a5452e4873567cabf1f3d1af52a0671711e51672630a4e5f2f0cfd5d9dbc2d'

	Creating transaction to fund job...

	    transaction:
		chainId: 42
		data: '0xef47243d'
		from: '0xFF2a327ed1Ca40CE93F116C5d6646b56991c0ddE'
		gas: 71246
		gasPrice: 1000000000
		nonce: 247
		to: '0x5f8Db0C6F8c7757d2dd43611Ef024419e153Df67'
		value: 0

	Proceed? (y/n): y
	Submitting transaction...

	    event_summaries:
	    -   args: {}
		event: JobFunded
	    receipt_summary:
		blockHash: '0x3382a58c68fdc515a9945098bf427376757470d8dcebd6ce7946d4d8d83b4fef'
		blockNumber: 8458614
		cumulativeGasUsed: 56246
		gasUsed: 56246
		transactionHash: '0x8efa41a9bb87d68d50bc7579421d258fd72009b3e5ba6215d843f42600c42e13'

	Signing job...

	Read call params from cmdline...

	Calling service...

	    response:
		value: 924.0
```

### 9.1 SNET-CLI: Calling the Service (local)
```
$ python3.6 test_call_basic_service.py 
Endpoint (localhost:7003): 
Method (add|sub|mul|div): mul
Number 1: 12
Number 2: 77
924.0

```
