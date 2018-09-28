#!/usr/bin/env python3
import socket
import sys

code = 'iso-8859-1'

# Auxiliary functions

def encode(data):
    return data.encode(code)

def decode(data):
    return data.decode()

#def writeRequest(request):
#    fullRequest = []

#    for word in request:
#        codedWord = encode(word)
#        fullRequest += [codedWord,]

#    return fullRequest
