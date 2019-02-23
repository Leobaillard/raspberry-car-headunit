#!/usr/bin/python

import socket
import sys

cmd = sys.argv[1]

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('', 8888))
s.send(cmd)
s.close()
