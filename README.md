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

- **SNET-CLI: Creating an Agent (The AI Service)**

-	snet agent-factory create-agent [price] [endpoint]
	 - `price` is the desired price for interacting with your service
		(a provided integer x is interpreted as x * 10^-8 AGI)
	 - `endpoint` is the endpoint on which your daemon is listening for requests
		(protocol and port are required)
```
	$ snet agent-factory create-agent 100 http://54.203.198.53:7000
	Create your first identity. This will be used to authenticate and sign requests pertaining
	to the blockchain.

	The available identity types are:
	    - 'rpc' (yields to a required ethereum json-rpc endpoint for signing using a given wallet
		  index)
	    - 'mnemonic' (uses a required bip39 mnemonic for HDWallet/account derivation and signing
		  using a given wallet index)
	    - 'key' (uses a required hex-encoded private key for signing)
	    - 'ledger' (yields to a required ledger nano s device for signing using a given wallet
		  index)
	    - 'trezor' (yields to a required trezor device for signing using a given wallet index)

	Create additional identities by running 'snet identity create', and switch identities by 
	running 'snet identity <identity_name>'.

	Choose a name for your first identity: 
	ARTUR_ID
	Select an identity type for your first identity (choose from ['rpc', 'mnemonic', 'key', 'trezor', 'ledger']): 
	key
	Private key: 

	set identity_name ARTUR_ID

	Creating transaction to create agent...

	    transaction:
		chainId: 42
		data: '...'
		from: '0xFF2a327ed1Ca40CE93F116C5d6646b56991c0ddE'
		gas: 1728995
		gasPrice: 1000000000
		nonce: 240
		to: '0x1fAa8ec70aFe4f5ce904dA935A6ddF5f3482eEDb'
		value: 0

	Proceed? (y/n): y
	Submitting transaction...

	    event_summaries:
	    -   args:
		    agent: '0xE0Ca10C9747426d18C46891eF51c578139D066fD'
		event: AgentCreated
	    receipt_summary:
		blockHash: '0xa5f28fbf4ba6c60ed49e871297abd516bbd6853bf67baa9758d402d6236fe3f2'
		blockNumber: 8458295
		cumulativeGasUsed: 1728995
		gasUsed: 1728995
		transactionHash: '0x73f3d503426a8a99b17dd145e3a43ba7e127e14f4e041c2900aec4cd86fecf43'

	set current_agent_at 0xE0Ca10C9747426d18C46891eF51c578139D066fD
```
- 	0xE0Ca10C9747426d18C46891eF51c578139D066fD is your agent's address.

- **SNET-CLI: Publishing the Service (of your Agent)**

-	snet service init
```	
	$ snet service init
	Please provide values to populate your service.json file

	Choose a name for your service: (default: "BasicService")

	Choose the path to your service's model directory: (default: "model/")

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
	    "model": "model/",
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
-	Now you have to create the 'model' folder and put the .proto file inside it.
```
	$ mkdir model
	$ cp basic_tamplate_rpc.proto model/
	$ ls -la model/
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

- 	Check the services from a specific Organization ('SNET_BH')
```
	$ snet contract Registry listServicesForOrganization SNET_BH
	[True, [b'BASIC_gRPC_ARITHMETIC_015\x00\x00\x00\x00\x00\x00\x00',
	b'ResNetService\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
	b'BasicService\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00']]

```
- **SNET-CLI: Removing an Agent (Set your service unavailable)**

-	snet contract Registry deleteServiceRegistration [organization] [name] --transact
	 - `organization` name of the Organization.
	 - `name` of the Agent.
```
	$ snet contract Registry deleteServiceRegistration SNET_BH BASIC_gRPC_ARITHMETIC_015 --transact
	    transaction:
		chainId: 42
		data: '...'
		from: '0xFF2a327ed1Ca40CE93F116C5d6646b56991c0ddE'
		gas: 127507
		gasPrice: 1000000000
		nonce: 244
		to: '0x440cF8424fcD7Fc2D2fF3a5668c919E93A3d2aAb'
		value: 0

	Proceed? (y/n): y
	Submitting transaction...

	    event_summaries:
	    -   args:
		    orgName: 534e45545f424800000000000000000000000000000000000000000000000000
		    orgNameIndexed: 534e45545f424800000000000000000000000000000000000000000000000000
		    serviceName: 42415349435f675250435f41524954484d455449435f30313500000000000000
		    serviceNameIndexed: 42415349435f675250435f41524954484d455449435f30313500000000000000
		event: ServiceDeleted
	    receipt_summary:
		blockHash: '0xb7a9cb6081f85e3e35f43b9819e4948f0a6239fe139204bd0795489dce411e4d'
		blockNumber: 8458422
		cumulativeGasUsed: 3241353
		gasUsed: 63754
		transactionHash: '0x44fbaaaad23c9773e534a78524b2e4aeb87ef640986c4e5dbf414a47b3f01250'
```
- **SNET-CLI: Checking you session**
```
	snet session
	    session:
		current_agent_at: 'YOU_AGENT_ADRESS'
		default_eth_rpc_endpoint: https://kovan.infura.io
		default_gas_price: '1000000000'
		default_wallet_index: '0'
		identity_name: ARTUR_ID
```
- **SNET-CLI: SET and UNSET**
-	If you need to change keys from your session.
```
	$ snet unset current_agent_at
	$ snet set current_agent_at 0x1591F7ecB3C4Fb2E57a2679c30aC8D9b4EC65248
```

### 8. SNET DAEMON: Running the service
-	Access your service endpoint and start the Daemon.

```
	$ git clone https://github.com/arturgontijo/snet_bh.git
	$ cd snet_bh/Snet_Services/gRPC/Basic_Template
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

### 9. SNET-CLI: Calling the Service

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
