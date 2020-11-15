#!/usr/bin/env python
# Last edit: 15/11/20
version = 1.

import unicornhat as uh
import time
import colorsys
import json
import socket
import requests


print("Booting v" + str(version))


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
	result = requests.get(f'https://www.markszulc.com', headers=headers, timeout=5)
	result.raise_for_status()
	jsonresult = result.json()

except requests.exceptions.Timeout as timeerr:
	printerror("The request for Graph API timed out! " + str(timeerr))

except requests.exceptions.HTTPError as err:
	if err.response.status_code == 404:
		printerror("MS Graph URL is invalid!")
		exit(5)
	elif err.response.status_code == 401:
		trycount = trycount + 1
		printerror("MS Graph is not authorized. Please reauthorize the app (401). Trial count: " + str(trycount))
		print()

except:
	print("Unexpected error:", sys.exc_info()[0])
	print("Will try again. Trial count: " + str(trycount))
	print()
	
