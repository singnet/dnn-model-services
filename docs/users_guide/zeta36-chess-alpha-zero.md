[issue-template]: ../../../issues/new?template=BUG_REPORT.md
[feature-template]: ../../../issues/new?template=FEATURE_REQUEST.md

![singnetlogo](../assets/singnet-logo.jpg?raw=true 'SingularityNET')

# Chess Alpha Zero

This service uses [Chess Alpha Zero](https://github.com/Zeta36/chess-alpha-zero)
 to play chess with reinforcement learning by AlphaGo Zero methods.

It is part of our third party [DNN Model Services](https://github.com/singnet/dnn-model-services).

### Welcome

The service receives a chess move as input, like `c2c4`.
This move means that the piece is at column `c` and row `2` and will move to
the position at column `c` and row `4`.

The model can detect illegal and end game moves.

### What’s the point?

The service uses deep neural network and reinforcement learning techniques to play chess.

The service outputs the best move that the pre-trained model supply.

### How does it work?

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

The user must provide the following inputs in order to play with the service:

Inputs:
  - `uid`: The user id to keep playing the same game (optional, 
  if not set the service will generate a random UID and send it back).
  - `move`: <col_1><row_1><col_2><row_2>.
     - <col_1>: column where the piece is.
     - <row_1>: row where the piece is.
     - <col_2>: column where the piece will be moved to.
     - <row_2>: row where the piece will be moved to.
  - `cmd`: A specific command to interact with the service (optional).
     - "restart": restart the game, keeping the UID.
     - "finish": finish the game, deleting the UID.

You can use this service from [SingularityNET DApp](http://beta.singularitynet.io/).

You can also call the service from SingularityNET CLI (`snet`).

Assuming that you have an open channel to this service:

```
$ snet client call snet zeta36-chess-alpha-zero default_group play '{"uid": "my_uid","move": "c2c4"}'

response:
UID: my_uid
board: 
    a b c d e f g h
-------------------
8 | r n b q k b n r
7 | p p p p . p p p
6 | . . . . . . . .
5 | . . . . p . . .
4 | . . P . . . . .
3 | . . . . . . . .
2 | P P . P P P P P
1 | R N B Q K B N R

status: game_running: e7e5
```

### What to expect from this service?

Inputs:
  - `uid`: 
  - `move`: "e2e4"
  - `cmd`: 

Response:
```
response:
UID: 9a7eae055435fa45df07
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
```

Inputs:
  - `uid`: "9a7eae055435fa45df07"
  - `move`: "a2a4"
  - `cmd`: 

Response:
```
response:
UID: 9a7eae055435fa45df07
board: 
    a b c d e f g h
-------------------
8 | r n b q k b n r
7 | p p . p p p . p
6 | . . . . . . p .
5 | . . p . . . . .
4 | P . . . P . . .
3 | . . . . . . . .
2 | . P P P . P P P
1 | R N B Q K B N R

status: game_running: g7g6
```