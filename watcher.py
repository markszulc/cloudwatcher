#!/usr/bin/env python
# Last edit: 15/11/20
version = 1.3

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
import unicornhat as uh
import threading
import sys
import urllib.parse
from time import sleep
from datetime import datetime, time
from signal import signal, SIGINT
from gpiozero import CPUTemperature
import pyqrcode

aioendpoint = 'https://runtime.adobe.io/api/v1/web/20092-cloudbuddy-stage/dx-excshell-1/buddyEndpoint'

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
sleepValue = 15 # seconds
spacing = 360.0 / 16.0




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

# Countdown for minutes
def countdown(t):
	total = t
	progvalue = 0
	while t:
		mins, secs = divmod(t, 60)
		timer = '{:02d}:{:02d}'.format(mins, secs)
		print("Time until next run: " + timer, end="\r")
		sleep(1)
		t -= 1
	print("                                      ", end="\r")


def switchBlue(prg) :
	rowoffset = prg * 3
	uh.set_pixel(2, 0, 0, 0, 0)
	uh.set_pixel(5, 0, 0, 0, 0)

	for x in range(2):
		offset = x + rowoffset
		for y in range(4):
			uh.set_pixel(offset, y, 50, 116, 222)
	uh.show()

def switchGreen(prg) :
	rowoffset = prg * 3
	uh.set_pixel(2, 0, 0, 0, 0)
	uh.set_pixel(5, 0, 0, 0, 0)
	for x in range(2):
		offset = x + rowoffset
		for y in range(4):
			uh.set_pixel(offset, y, 0, 255, 0)
	uh.show()
	
def switchOrange(prg) :
	rowoffset = prg * 3
	uh.set_pixel(2, 0, 0, 0, 0)
	uh.set_pixel(5, 0, 0, 0, 0)
	for x in range(2):
		offset = x + rowoffset
		for y in range(4):
			uh.set_pixel(offset, y, 255, 165, 0)
	uh.show()

	


#### MAIN ######
while True:
	# Check internet
	if is_connected == False:
		printerror("No network. Please connect to the internet and restart the app.")
		exit(3)


	uh.set_layout(uh.PHAT)
	uh.brightness(0.5)
	uh.set_pixel(2, 0, 100,100,100)
	uh.set_pixel(5, 0, 100, 100, 100)
	uh.show()



	print("Fetching new data")
	headers={}

	jsonresult = ''
	trycount = 0

	try:
		result = requests.get(aioendpoint, headers=headers, timeout=5)
		result.raise_for_status()
		jsonresult = result.json()
		print(jsonresult)

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
	# os.system('clear')
	print("============================================")
	print("            Cloud Buddy")
	print("============================================")
	print()
	now = datetime.now()
	print("Last API call:\t\t" + now.strftime("%Y-%m-%d %H:%M:%S"))
	cpu_r = round(cpu.temperature, 2)
	print("Current CPU:\t\t" + str(cpu_r) + "°C")
			
	try: 	
		print("Parsing data... ")
		print(jsonresult)
		print(jsonresult['Environments'])
		print(jsonresult['Environments'][0])

		for item in jsonresult["Environments"]:
			print("found item: " + item)

		if jsonresult['name'] == "John Doe":
					print("I saw John:\t\t" + '\033[31m' + "Hibernated" + '\033[0m')
					switchBlue(2)

		# elif jsonresult['name'] == "Jane Doe":
		# 			print("Nevarro Dev:\t\t" + '\033[32m' + "Running" + '\033[0m')
		# 			switchGreen(2)

		# elif jsonresult['cm-p31363-e105601']['state'] == "starting":
		# 			print("Nevarro Dev:\t\t" + '\033[30m' + "De-Hibernating" + '\033[0m')
		# 			switchOrange(2)

		# if jsonresult['cm-p47527-e236969']['state'] == "hibernated":
		# 			print("Scariff Dev:\t\t" + '\033[31m' + "Hibernated" + '\033[0m')
		# 			switchBlue(1)

		# elif jsonresult['cm-p47527-e236969']['state'] == "running":
		# 			print("Scariff Dev:\t\t" + '\033[32m' + "Running" + '\033[0m')
		# 			switchGreen(1)

		# elif jsonresult['cm-p47527-e236969']['state'] == "starting":
		# 			print("Scariff Dev:\t\t" + '\033[30m' + "De-Hibernating" + '\033[0m')
		# 			switchOrange(1)

		# if jsonresult['cm-p24704-e76433']['state'] == "hibernated":
		# 			print("WKND Dev:\t\t" + '\033[31m' + "Hibernated" + '\033[0m')
		# 			switchBlue(0)

		# elif jsonresult['cm-p24704-e76433']['state'] == "running":
		# 			print("WKND Dev:\t\t" + '\033[32m' + "Running" + '\033[0m')
		# 			switchGreen(0)

		# elif jsonresult['cm-p24704-e76433']['state'] == "starting":
		# 			print("WKND Dev:\t\t" + '\033[30m' + "De-Hibernating" + '\033[0m')
		# 			switchOrange(0)
	except:
		print("Unable to fetch status")
				
	print(" ")			
				
	countdown(int(sleepValue))
