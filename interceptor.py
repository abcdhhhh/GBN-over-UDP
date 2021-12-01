from socket import socket, AF_INET, SOCK_DGRAM
import os
import random
import time
import argparse
from common import MTU

parser = argparse.ArgumentParser()

parser.add_argument('--fromSenderPort', type=int, default=1600)
parser.add_argument('--toSenderPort', type=int, default=1601)
parser.add_argument('--fromReceiverPort', type=int, default=1602)
parser.add_argument('--toReceiverPort', type=int, default=1603)
parser.add_argument('--corruptionRate', type=float, default=0.0)
parser.add_argument('--dropRate', type=float, default=0.0)
args = parser.parse_args()
fromSenderAddr = ('localhost', args.fromSenderPort)
toSenderAddr = ('localhost', args.toSenderPort)
fromReceiverAddr = ('localhost', args.fromReceiverPort)
toReceiverAddr = ('localhost', args.toReceiverPort)
corruptionRate = float(args.corruptionRate)
dropRate = args.dropRate


def usage():
    print("Usage: python interceptor.py FromSenderPort ToReceiverPort FromReceiverPort ToSenderPort")
    exit()


def randSleep():
    # Sleep for a uniformly random amount of time between 80 and 120ms.
    delay = random.random() * 0.4 + 0.8
    time.sleep(delay)


def corrupt(pkt):
    # bytes -> bytes
    # corrupt a packet
    index = random.randint(0, len(pkt) - 1)
    pkt = pkt[:index] + os.urandom(1) + pkt[index + 1:]
    return pkt


def intercept(pkt, outSock, addr):
    if random.random() < dropRate:
        print("Dropped")
        return
    if random.random() < corruptionRate:
        print("Corrupted")
        pkt = corrupt(pkt)
    # randSleep()
    outSock.sendto(pkt, addr)


fromSenderSock = socket(AF_INET, SOCK_DGRAM)
fromSenderSock.bind(fromSenderAddr)
fromSenderSock.setblocking(0)
fromReceiverSock = socket(AF_INET, SOCK_DGRAM)
fromReceiverSock.bind(fromReceiverAddr)
fromReceiverSock.setblocking(0)

outSock = socket(AF_INET, SOCK_DGRAM)

print("Listening...")
while True:
    try:
        pkt = fromSenderSock.recv(MTU)
        # print("Received packet from sender:", pkt)
        intercept(pkt, outSock, toReceiverAddr)
    except:
        pass
    try:
        pkt = fromReceiverSock.recv(MTU)
        # print("Received packet from receiver:", pkt)
        intercept(pkt, outSock, toSenderAddr)
    except:
        pass
