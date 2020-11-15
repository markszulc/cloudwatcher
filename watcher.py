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
	
	
def switchOff() :
	global blinkThread, globalBlue, globalGreen, globalRed
	globalRed = 0
	globalGreen = 0
	globalBlue = 0
	if blinkThread != None :
		blinkThread.do_run = False
	unicorn.clear()
	unicorn.off()

class LightPoint:

	def __init__(self):
		self.direction = randint(1, 4)
		if self.direction == 1:
			self.x = randint(0, width - 1)
			self.y = 0
		elif self.direction == 2:
			self.x = 0
			self.y = randint(0, height - 1)
		elif self.direction == 3:
			self.x = randint(0, width - 1)
			self.y = height - 1
		else:
			self.x = width - 1
			self.y = randint(0, height - 1)

		self.colour = []
		for i in range(0, 3):
			self.colour.append(randint(100, 255))


def update_positions():

	for point in points:
		if point.direction == 1:
			point.y += 1
			if point.y > height - 1:
				points.remove(point)
		elif point.direction == 2:
			point.x += 1
			if point.x > width - 1:
				points.remove(point)
		elif point.direction == 3:
			point.y -= 1
			if point.y < 0:
				points.remove(point)
		else:
			point.x -= 1
			if point.x < 0:
				points.remove(point)


def plot_points():

	unicorn.clear()
	for point in points:
		unicorn.set_pixel(point.x, point.y, point.colour[0], point.colour[1], point.colour[2])
	unicorn.show()

def blinkRandom(arg):
	t = threading.currentThread()
	while getattr(t, "do_run", True):
		if len(points) < 10 and randint(0, 5) > 1:
			points.append(LightPoint())
		plot_points()
		update_positions()
		sleep(0.03)
	


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
			switchBlue()
		elif jsonresult['status'] == "running":
			print("Venia Dev:\t\t" + '\033[31m' + "Running" + '\033[0m')
			switchBlue()
			
			
			
#print(jsonresult['status'])
#switchBlue()
