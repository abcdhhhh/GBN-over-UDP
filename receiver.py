from socket import socket, AF_INET, SOCK_DGRAM
# from sys import stdout
from common import packet, str2packet, MSS, MTU
import argparse


def send_ack(acknum: int, to):
    pkt = packet(0, acknum, '0' * MSS)
    pkt.checksum = pkt.get_checksum()
    send_sock.sendto(pkt.tostr().encode(), to)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--dest_addr', default='127.0.0.1')
    parser.add_argument('--dest_port', type=int, default=1602)
    parser.add_argument('--listen_addr', default='127.0.0.1')
    parser.add_argument('--listen_port', type=int, default=1603)
    parser.add_argument('filename')
    args = parser.parse_args()

    dest_addr = args.dest_addr
    dest_port = args.dest_port
    dest = (dest_addr, dest_port)
    listen_addr = args.listen_addr
    listen_port = args.listen_port
    listen = (listen_addr, listen_port)
    filename = args.filename

    send_sock = socket(AF_INET, SOCK_DGRAM)
    recv_sock = socket(AF_INET, SOCK_DGRAM)

    recv_sock.bind(listen)
    # init
    expecting_seq = 1
    fp = open('./received/' + filename, 'wb')

    while True:
        message, address = recv_sock.recvfrom(MTU)
        # get packet
        negative_seq = expecting_seq - 1
        try:
            pkt = str2packet(message.decode())
        except:
            print(f"Packet corrupted. send ack{negative_seq}")
            send_ack(negative_seq, dest)
        else:
            if pkt.get_checksum() != pkt.checksum:
                print(f"Packet corrupted. send ack{negative_seq}")
                send_ack(negative_seq, dest)
            elif pkt.seqnum != expecting_seq:
                print(f"Not the expecting seq (expected {expecting_seq}, got {pkt.seqnum}. send ack{negative_seq})")
                send_ack(negative_seq, dest)
            else:
                # print(f"receive message: {pkt.payload}")
                print(f"send ack{expecting_seq}")
                fp.write(pkt.payload.encode())
                send_ack(expecting_seq, dest)
                if pkt.acknum:
                    # is_end
                    break
                expecting_seq += 1
    fp.close()
