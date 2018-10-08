#!/usr/bin/env python3
import socket
import sys
import datetime

code = 'iso-8859-1'

# Auxiliary functions

def encode(data):
    return data.encode(code)

def decode(data):
    return data.decode()

def dateEpoch(dateString):
    dateNumbers = dateString.split('.')
    timestamp = datetime.datetime(int(dateNumbers[2]), int(dateNumbers[1]), int(dateNumbers[0]), 0, 0).timestamp()
    return timestamp

def timeEpoch(timeString):
    timeNumbers = timeString.split(':')
    timestamp = float(timeNumbers[2]) + float(timeNumbers[1])*60 + float(timeNumbers[0])*3600
    return timestamp 

