# -*- coding: utf-8 -*-
"""
Created on Tue Mar 21 11:31:22 2023

@author: NelsonChunManTo
"""

import socket

s = socket.socket()
s.connect(('192.168.0.200', 2001))
s.send('< >'.encode())
print (s.recv(1024).decode())
s.close()
