import zmq
import os
import sys
import time
from multiprocessing import Process
import random
import multiprocessing
from queue import Queue

def sendFailure(msg, proposer, prob, socket):
    if random.random() < prob:
        msg = "CRASH" + " " + str(proposer)
    socket.send_string(msg)

def broadcastFailure(msg, proposer, N, prob, sockets):
    for num in range(N):
        sendFailure(msg, proposer, prob, sockets[num])


def PaxosNodes(ID, prob, N, val, numRounds, printLock):
    maxVotedRound = -1
    maxVotedVal = None
    decision = None
    proposeVal = None
    MsgQ = Queue()
    context = zmq.Context()
    mysocket = context.socket(zmq.PULL)
    localhost = "127.0.0.1"
    myport = 5550 + ID
    myport = str(myport)
    mysocket.bind(f"tcp://{localhost}:{myport}")
    time.sleep(0.5)
    sockets = []
    for num in range(N+1):
        port = 5550 + num
        port = str(port)
        socket = context.socket(zmq.PUSH)
        socket.connect(f"tcp://{localhost}:{port}")
        sockets.append(socket)
    time.sleep(0.5)
    for num in range(numRounds):
        if num % N == ID:
            printLock.acquire()
            print(f"ROUND {num} STARTED WITH INITIAL VALUE {val}")
            printLock.release()
            broadcastFailure("START", ID, N, prob, sockets)
            joincount = 0
            temp_max_round = -1
            temp_max_val = -1
            for i in range(N):
                message = mysocket.recv_string()
                printLock.acquire()
                print(f"LEADER OF {num} RECEIVED IN JOIN PHASE: {message}")
                printLock.release()
                message = message.split()
                if message[0] == "START":
                    joincount = joincount + 1
                    if maxVotedRound > temp_max_round:
                        temp_max_round = maxVotedRound
                        temp_max_val = maxVotedVal
                elif message[0] == "JOIN":
                    joincount = joincount + 1
                    message[1] = int(message[1])
                    if message[1] > temp_max_round:
                        temp_max_round = message[1]
                        temp_max_val = message[2]
            if joincount > N/2:
                if temp_max_round == -1:
                    proposeVal = val
                else:
                    proposeVal = temp_max_val
                msg = "PROPOSE " + str(proposeVal)
                broadcastFailure(msg, ID, N, prob, sockets)
                votecount = 0
                replycount = 0
                while replycount < N:
                    vote = mysocket.recv_string()
                    votes = vote.split()
                    if votes[0] == "PROPOSE" or votes[0] == "VOTE":
                        replycount = replycount + 1
                        printLock.acquire()
                        print(f"LEADER OF {num} RECEIVED IN VOTE PHASE: {vote}")
                        printLock.release()
                    elif votes[0] == "CRASH":
                        if int(votes[1]) != ID: 
                            MsgQ.put(vote)
                        else:
                            replycount = replycount + 1
                            printLock.acquire()
                            print(f"LEADER OF {num} RECEIVED IN VOTE PHASE: {vote}")
                            printLock.release()
                    else:
                        MsgQ.put(vote)
                    if votes[0] == "PROPOSE":
                        votecount = votecount + 1
                        maxVotedRound = num 
                        maxVotedVal = proposeVal
                    elif votes[0] == "VOTE":
                        votecount = votecount + 1
                if votecount > N/2:
                    decision = proposeVal
                    printLock.acquire()
                    print(f"LEADER OF {num} DECIDED ON VALUE {decision}")
                    printLock.release()
            else:
                printLock.acquire()
                print(f"LEADER OF ROUND {num} CHANGED ROUND")
                printLock.release()
                for k in range(N):
                    if k != ID:
                        sockets[k].send_string("ROUNDCHANGE")
        else:
            if (MsgQ.empty()):
                message = mysocket.recv_string()
            else:
                message = MsgQ.get()
            printLock.acquire()
            print(f"ACCEPTOR {ID} RECEIVED IN JOIN PHASE: {message}")
            printLock.release()
            message = message.split()
            if message[0] == "START":
                reply = "JOIN " + str(maxVotedRound) + " " + str(maxVotedVal)
                sendFailure(reply, num % N, prob, sockets[num % N])
            else:
                reply = "CRASH " + str(num % N)
                sockets[num % N].send_string(reply)
            proposal = mysocket.recv_string()
            temp_split = proposal.split()
            if temp_split[0] == "START":
                MsgQ.put(proposal)
                proposal = mysocket.recv_string()
            elif temp_split[0] == "CRASH":
                if int(temp_split[1]) != (num%N):
                    MsgQ.put(proposal)
                    proposal = mysocket.recv_string()
            printLock.acquire()
            print(f"ACCEPTOR {ID} RECEIVED IN VOTE PHASE: {proposal}")
            printLock.release()
            proposal = proposal.split()
            if proposal[0] == "PROPOSE":
                reply = "VOTE"
                sendFailure(reply, num % N, prob, sockets[num % N])
                maxVotedRound = num
                maxVotedVal = proposal[1]
            elif proposal[0] == "CRASH":
                reply = "CRASH " + str(num % N)
                sockets[num % N].send_string(reply)





if __name__ == '__main__':
    n = len(sys.argv)
    if n != 4:
        print("Four arguments expected")
        sys.exit(1)

    num_nodes = int(sys.argv[1])
    crash_prob = float(sys.argv[2])
    num_rounds = int(sys.argv[3])
    nodes = []
    printLock = multiprocessing.Lock()
    print(f"NUM_NODES: {num_nodes}, CRASH_PROB: {crash_prob}, NUM_ROUNDS: {num_rounds}")
    for num in range(num_nodes):
        node = Process(target=PaxosNodes, args= (num, crash_prob, num_nodes, random.randrange(2), num_rounds, printLock))
        nodes.append(node)
    for node in nodes:
        node.start()
    for node in nodes:
        node.join()
