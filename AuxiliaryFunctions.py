#!/usr/bin/env python3
import socket
import sys

code = 'iso-8859-1'

# Auxiliary functions

def encode(data):
    return data.encode(code)

def decode(data):
    return data.decode()

