[issue-template]: ../../../../../issues/new?template=BUG_REPORT.md
[feature-template]: ../../../../../issues/new?template=FEATURE_REQUEST.md

![singnetlogo](../../docs/assets/singnet-logo.jpg 'SingularityNET')

# Chess Alpha Zero

This service uses [Chess Alpha Zero](https://github.com/Zeta36/chess-alpha-zero)
 to play chess with reinforcement learning by AlphaGo Zero methods.

It is part of our third party [DNN Model Services](https://github.com/singnet/dnn-model-services).

## Getting Started

### Requirements

- [Python 3.6.5](https://www.python.org/downloads/release/python-365/)
- [SNET CLI](https://github.com/singnet/snet-cli)

### Development

Clone this repository:

```
$ git clone https://github.com/singnet/dnn-model-services.git
$ cd dnn-model-services/services/zeta36-chess-alpha-zero
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
   "DAEMON_END_POINT": "0.0.0.0:7058",
   "IPFS_END_POINT": "http://ipfs.singularitynet.io:80",
   "BLOCKCHAIN_NETWORK_SELECTED": "ropsten",
   "PASSTHROUGH_ENABLED": true,
   "PASSTHROUGH_ENDPOINT": "http://localhost:7003",
   "ORGANIZATION_ID": "snet",
   "SERVICE_ID": "zeta36-chess-alpha-zero",
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
$ pip3.6 install -r requirements.txt
```

Generate the gRPC codes:
```
$ sh buildproto.sh
```

Clone the `chess-alpha-zero` repository:
```
$ git clone https://github.com/Zeta36/chess-alpha-zero.git
```

Start the service and `SNET Daemon`:
```
$ python3.6 run_alpha_zero_service.py
```

### Calling the service:

The board has this layout:
```
    a b c d e f g h
-------------------
8 | r n b q k b n r
7 | p p p p p p p p
6 | . . . . . . . .
5 | . . . . . . . .
4 | . . . . . . . .
3 | . . . . . . . .
2 | P P P P P P P P
1 | R N B Q K B N R
```

Uppercase letters are white pieces and lowercase are black.

Each letter represents the following pieces:

```
P|p: pawns
R|r: rooks
N|n: knights
B|b: bishops
Q|q: queens
K|k: kings
```

Inputs:
  - `uid`: The user id to keep playing the same game (optional, 
  if not set the service will generate a random UID and send it back).
  - `move`: <col_1><row_1><col_2><row_2>.
     - <col_1>: column where the piece is.
     - <row_1>: row where the piece is.
     - <col_2>: column to where the piece will be moved.
     - <row_2>: row to where the piece will be moved.
  - `cmd`: A specific command to interact with the service (optional).
     - "restart": restart the game, keeping the UID.
     - "finish": finish the game, deleting the UID.

Local (testing purpose):

```
$ python3.6 test_alpha_zero_service.py 
Endpoint (localhost:7003): 
Method (play): 
UID (empty): human_player
Move (e2e4): 
CMD (empty): 

response:
UID: artur
board: 
    a b c d e f g h
-------------------
8 | r n b q k b n r
7 | p p . p p p p p
6 | . . . . . . . .
5 | . . p . . . . .
4 | . . . . P . . .
3 | . . . . . . . .
2 | P P P P . P P P
1 | R N B Q K B N R

status: game_running: c7c5

$ python3.6 test_alpha_zero_service.py 
Endpoint (localhost:7003): 
Method (play): 
UID (empty): human_player
Move (e2e4): d2d3
CMD (empty): 

response:
UID: artur
board: 
    a b c d e f g h
-------------------
8 | r n b q k b n r
7 | p p . p p p . p
6 | . . . . . . p .
5 | . . p . . . . .
4 | . . . . P . . .
3 | . . . P . . . .
2 | P P P . . P P P
1 | R N B Q K B N R

status: game_running: g7g6
```

Through SingularityNET (follow this [link](https://dev.singularitynet.io/tutorials/publish/) to learn how to publish a service and open a payment channel to be able to call it):

Assuming that you have an open channel to this service:

```
$ snet client call snet zeta36-chess-alpha-zero default_group play '{"move": "g1f3"}'

response:
UID: b8f24aa8f25a5dddbfaf
board: 
    a b c d e f g h
-------------------
8 | r n b q k b n r
7 | p p . p p p p p
6 | . . . . . . . .
5 | . . p . . . . .
4 | . . . . . . . .
3 | . . . . . N . .
2 | P P P P P P P P
1 | R N B Q K B . R

status: game_running: c7c5
```

## Contributing and Reporting Issues

Please read our [guidelines](https://dev.singularitynet.io/docs/contribute/contribution-guidelines/#submitting-an-issue) before submitting an issue. If your issue is a bug, please use the bug template pre-populated [here][issue-template]. For feature requests and queries you can use [this template][feature-template].

## Authors

* **Artur Gontijo** - *Maintainer* - [SingularityNET](https://www.singularitynet.io)
