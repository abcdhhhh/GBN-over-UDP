MSS = 1024
MTU = 24 + MSS
WINDOW_SIZE = 10


class packet:
    def __init__(self, seqnum, acknum, payload, checksum=0):
        # int(8), int(8), str(MSS)
        self.seqnum = seqnum
        self.acknum = acknum
        self.payload = payload
        self.checksum = checksum

    def get_checksum(self):
        checksum = self.seqnum + self.acknum
        checksum = (checksum & 0xffffffff) + (checksum >> 32)
        length = len(self.payload)
        for i in range(0, length):
            checksum += ord(self.payload[i]) << i % 4 * 8
            checksum = (checksum & 0xffffffff) + (checksum >> 32)
        return checksum

    def tostr(self):
        return "{:<8x}{:<8x}{:<8x}{}".format(self.checksum, self.seqnum, self.acknum, self.payload)


def str2packet(s):
    checksum = int(s[0:8], 16)
    seqnum = int(s[8:16], 16)
    acknum = int(s[16:24], 16)
    payload = s[24:]
    return packet(seqnum, acknum, payload, checksum)
