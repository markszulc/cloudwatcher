#!/usr/bin/env python
# Last edit: 15/11/20
version = 1.

import requests
import socket
import atexit
import os
import os.path
import argparse
from random import randint
import configparser
from urllib.error import HTTPError
import json
import unicornhat as unicorn
import threading
import sys
import urllib.parse
from time import sleep
from datetime import datetime, time
from signal import signal, SIGINT
from gpiozero import CPUTemperature
import pyqrcode


print("Booting v" + str(version))

width = 0
height = 0
blinkThread = None
after_work = False
globalRed = 0
globalGreen = 0
globalBlue = 0
token=''
points = []
fullname = ''
brightness_led = 0.5
sleepValue = 30 # seconds




# Define Error Logging
def printerror(ex):
	print('\033[31m' + str(ex) + '\033[0m')

# Check or internet connection
def is_connected():
    try:
        # connect to the host -- tells us if the host is actually
        # reachable
        socket.create_connection(("www.google.com", 80))
        return True
    except OSError:
        pass
    return False


#### MAIN ######

# Check internet
if is_connected == False:
	printerror("No network. Please connect to the internet and restart the app.")
	exit(3)


	
print("Fetching new data")
headers={}

jsonresult = ''
trycount = 0

try:
	result = requests.get(f'https://runtime.adobe.io/api/v1/web/20092_29243/PreciousOrangeHorse-0.0.1/generic', headers=headers, timeout=5)
	result.raise_for_status()
	jsonresult = result.json()

except requests.exceptions.Timeout as timeerr:
	printerror("The request for Cloud Buddy API timed out! " + str(timeerr))

except requests.exceptions.HTTPError as err:
	if err.response.status_code == 404:
		printerror("Cloud Buddy URL is invalid!")
		exit(5)
	elif err.response.status_code == 401:
		trycount = trycount + 1
		printerror("Cloud Watcher is not authorized. Please reauthorize the app (401). Trial count: " + str(trycount))
		print()

except:
	print("Unexpected error:", sys.exc_info()[0])
	print("Will try again. Trial count: " + str(trycount))
	print()
	
	
# Get CPU temp
cpu = CPUTemperature()

# Print to display
#os.system('clear')
print("============================================")
print("            Cloud Watcher")
print("============================================")
print()
now = datetime.now()
print("Last API call:\t\t" + now.strftime("%Y-%m-%d %H:%M:%S"))
cpu_r = round(cpu.temperature, 2)
print("Current CPU:\t\t" + str(cpu_r) + "°C")

if jsonresult['status'] == "hibernated":
			print("Venia Dev:\t\t" + '\033[32m' + "Hibernated" + '\033[0m')

elif jsonresult['status'] == "running":
			print("Venia Dev:\t\t" + '\033[31m' + "Running" + '\033[0m')
			
			
			
print(jsonresult['status'])
