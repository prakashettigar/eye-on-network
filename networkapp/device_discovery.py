import sys
import subprocess
import os
import multiprocessing.dummy
import multiprocessing
import socket
import struct

class DEVICEDISCOVERY:
    def __init__(self):
        self.ping_res={}
        self.activedevice_count=0
        self.inactivedevice_count=0

    def ips(self,start, end):
        start = struct.unpack('>I', socket.inet_aton(start))[0]
        end = struct.unpack('>I', socket.inet_aton(end))[0]
        return [socket.inet_ntoa(struct.pack('>I', i)) for i in range(start, end)]


    def ping(self,ip):
        with open(os.devnull, "wb") as limbo:
            result = subprocess.Popen(
                ["ping", "-n", "1", "-w", "2", ip], stdout=limbo, stderr=limbo).wait()
            if result:
                self.ping_res.update({ip: "inactive"})
                self.inactivedevice_count += 1
            else:
                self.ping_res.update({ip: "active"})
                self.activedevice_count += 1

    def ping_range(self,list):
        num_threads = 2 * multiprocessing.cpu_count()
        p = multiprocessing.dummy.Pool(num_threads)
        p.map(self.ping,list)
