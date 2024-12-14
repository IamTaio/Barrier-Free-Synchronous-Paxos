# Synchronous Paxos Consensus Implementation

## 1. Project Overview
This project implements a synchronous version of the Paxos consensus algorithm for distributed systems. The implementation allows multiple nodes to agree on a binary value (0 or 1) while tolerating node failures.

Key features:
- Synchronous communication between nodes
- Probabilistic crash failure simulation
- Barrier-free implementation
- Round-robin leadership rotation
- Built using Python and ZeroMQ

## 2. Problem Statement
### Problem
Implement a binary consensus protocol where distributed nodes must agree on a single binary value while tolerating node failures in a synchronous system.

### Requirements
The implementation must satisfy:
- Agreement: All nodes that decide must choose the same value
- Validity: The decided value must be one of the initially proposed values
- Fault Tolerance: System continues despite node failures

### Input
Command line arguments:
```bash
python paxos.py <num_nodes> <crash_probability> <num_rounds>
```
- num_nodes: Number of Paxos nodes (integer)
- crash_probability: Probability of node failure (float between 0-1)
- num_rounds: Number of consensus rounds to run (integer)

Example:
```bash
python paxos.py 4 0.1 3
```

### Output
The program outputs the progression of the consensus protocol, including:
- Round starts
- Message receipts
- Decisions made
- Round changes

Example output:
```
NUM_NODES: 4, CRASH_PROB: 0.1, NUM_ROUNDS: 3
ROUND 0 STARTED WITH INITIAL VALUE: 1
LEADER OF 0 RECEIVED IN JOIN PHASE: START
ACCEPTOR 2 RECEIVED IN JOIN PHASE: START
LEADER OF 0 RECEIVED IN JOIN PHASE: JOIN -1 None
...
LEADER OF 0 DECIDED ON VALUE: 1
```

## 3. Implementation Details

### Core Components
1. **Network Layer**
   - ZeroMQ PUSH/PULL sockets
   - Each node has 1 PULL socket for receiving
   - Each node has N PUSH sockets for sending

2. **Node States**
   - maxVotedRound: Highest round voted in
   - maxVotedVal: Value voted for in maxVotedRound
   - proposeVal: Current proposed value
   - decision: Decided value (if any)

### Key Functions
```python
def sendFailure(msg, proposer, prob, socket):
    # Sends message with probability of failure
    
def broadcastFailure(msg, proposer, N, prob, sockets):
    # Broadcasts message to all nodes
    
def PaxosNodes(ID, prob, N, val, numRounds, printLock):
    # Main node logic implementation
```

### Protocol Phases
1. Join Phase
   - Leader broadcasts START
   - Collects JOIN responses
   - Requires majority to proceed

2. Propose Phase
   - Leader proposes value
   - Collects votes
   - Decides if majority obtained

## 4. Usage Instructions

### Requirements
- Python 3.x
- ZeroMQ library (`pip install zmq`)

### Running the Program
1. Install dependencies:
```bash
pip install zmq
```

2. Run the program:
```bash
python paxos.py <num_nodes> <crash_prob> <num_rounds>
```

Example:
```bash
python paxos.py 5 0.2 10
```

## 5. Error Handling
- Validates command line arguments
- Handles node failures through CRASH messages
- Manages message queue for out-of-order messages
- Tolerates up to N/2 node failures

### Limitations
- All nodes must be on the same machine (localhost)
- Requires proper command line arguments
- Performance may degrade with high crash probability

## 6. Example Session
```bash
$ python paxos.py 4 0.1 3
NUM_NODES: 4, CRASH_PROB: 0.1, NUM_ROUNDS: 3
ROUND 0 STARTED WITH INITIAL VALUE: 1
LEADER OF 0 RECEIVED IN JOIN PHASE: START
ACCEPTOR 2 RECEIVED IN JOIN PHASE: START
LEADER OF 0 RECEIVED IN JOIN PHASE: JOIN -1 None
ACCEPTOR 1 RECEIVED IN JOIN PHASE: START
LEADER OF 0 RECEIVED IN JOIN PHASE: JOIN -1 None
LEADER OF 0 DECIDED ON VALUE: 1
...
```

This example shows:
1. System initialization
2. First round execution
3. Successful consensus achievement
4. Message exchange between nodes

The program continues executing rounds until reaching the specified number of rounds or all nodes terminate.
