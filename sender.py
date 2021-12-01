from socket import socket, AF_INET, SOCK_DGRAM, timeout
from common import packet, str2packet, MSS, MTU, WINDOW_SIZE
import argparse
import time

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--dest_addr', default='127.0.0.1')
    parser.add_argument('--dest_port', type=int, default=1600)
    parser.add_argument('--listen_addr', default='127.0.0.1')
    parser.add_argument('--listen_port', type=int, default=1601)
    parser.add_argument('filename')
    args = parser.parse_args()

    dest_addr = args.dest_addr
    dest_port = args.dest_port
    dest = (dest_addr, dest_port)
    listen_addr = args.listen_addr
    listen_port = args.listen_port
    listen = (listen_addr, listen_port)
    filename = args.filename

    with open(filename, 'rb') as f:
        content = f.read().decode()  # str

    send_sock = socket(AF_INET, SOCK_DGRAM)
    recv_sock = socket(AF_INET, SOCK_DGRAM)

    recv_sock.bind(listen)
    recv_sock.settimeout(1)

    num_trans = 0

    def send_pkt(seqnum: int):
        # print(f"send pkt {seqnum}")
        global num_trans, content, send_sock, dest
        num_trans += 1
        left = seqnum * MSS
        is_end = 0
        right = left + MSS
        if right >= len(content):
            right = len(content)
            is_end = 1
        segment = content[left:right]
        # print(f"send: {segment}")
        sndpkt = packet(seqnum + 1, is_end, segment)
        sndpkt.checksum = sndpkt.get_checksum()
        b = sndpkt.tostr().encode()
        # print(send_sock)
        send_sock.sendto(b, dest)

    def send_range(left_num: int, right_num: int):
        global content, send_sock, dest
        print(f"send range [{left_num}, {right_num})")
        for i in range(left_num, right_num):
            send_pkt(i)

    # init
    # offset = 0
    # base = 0
    # nextseqnum = 0

    # num_accurate = 0
    # total_rtt = 0
    total_num = (len(content) - 1) // MSS + 1
    left_num = 0
    right_num = min(WINDOW_SIZE, total_num)
    start_time = time.time()

    # receive segments
    send_range(left_num, right_num)
    while left_num < right_num:
        try:
            message, address = recv_sock.recvfrom(MTU)
        except timeout:
            print("Timeout")
            if (left_num + 1 == total_num):
                break
            send_range(left_num, right_num)

        else:
            try:
                pkt = str2packet(message.decode())
            except:
                print("Packet corrupted. drop.")
            else:
                if pkt.get_checksum() != pkt.checksum:
                    print("Packet corrupted. drop.")
                elif pkt.acknum - 1 < left_num:
                    print(f"Not expected seq (expected {left_num}, got {pkt.acknum-1})")
                else:
                    print(f"acked {pkt.acknum-1}")
                    left_num = pkt.acknum - 1
                    while right_num < total_num and right_num < left_num + WINDOW_SIZE - 1:
                        send_pkt(right_num)
                        right_num += 1
    end_time = time.time()

    print(f"packet loss rate: {1-total_num/num_trans}")
    print(f"total time:{end_time-start_time}")
