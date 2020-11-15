#!/usr/bin/env python
# Last edit: 15/11/20
version = 1.

import os
import unicornhat as uh
import time
import colorsys
import json
import socket
import requests
from gpiozero import CPUTemperature
from time import sleep
from datetime import datetime, time
import threading	


print("Booting v" + str(version))

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

# ############################
#        UNICORN SETUP
# ############################
def setColor(r, g, b, brightness, speed) :
	global crntColors, globalBlue, globalGreen, globalRed
	globalRed = r
	globalGreen = g
	globalBlue = b

	if brightness == '' :
		unicorn.brightness(brightness_led)

	for y in range(height):
		for x in range(width):
			unicorn.set_pixel(x, y, r, g, b)
			unicorn.show()

def pulse():
	for b in range(0, 7):
		blockPrint()
		unicorn.brightness(b/10)
		enablePrint()
		for y in range(height):
			for x in range(width):
				unicorn.set_pixel(x, y, 102, 255, 255)
				unicorn.show()
		sleep(0.05)
	sleep(1)
	for b in range(6, 0, -1):
		blockPrint()
		unicorn.brightness(b/10)
		enablePrint()
		for y in range(height):
			for x in range(width):
				unicorn.set_pixel(x, y, 102, 255, 255)
				unicorn.show()
		sleep(0.05)

def switchBlue() :
	red = 0
	green = 0
	blue = 250
	blinkThread = threading.Thread(target=setColor, args=(red, green, blue, '', ''))
	blinkThread.do_run = True
	blinkThread.start()
	
	


#### MAIN ######

# Check internet
if is_connected == False:
	printerror("No network. Please connect to the internet and restart the app.")
	exit(3)

	
# Setup Unicorn light
setColor(50, 50, 50, 1, '')
unicorn.set_layout(unicorn.AUTO)
unicorn.brightness(0.5)

# Get the width and height of the hardware
width, height = unicorn.get_shape()

blinkThread = threading.Thread(target=blinkRandom, args=("task",))
blinkThread.do_run = True
blinkThread.start()

	
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
os.system('clear')
print("============================================")
print("            Cloud Watcher")
print("============================================")
print()
now = datetime.now()
print("Last API call:\t\t" + now.strftime("%Y-%m-%d %H:%M:%S"))
cpu_r = round(cpu.temperature, 2)
print("Current CPU:\t\t" + str(cpu_r) + "°C")

print(jsonresult['status'])
