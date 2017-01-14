#!/usr/bin/python

# Logging and daemon instanciatiation following this:
# 	http://blog.scphillips.com/2013/07/getting-a-python-script-to-run-in-the-background-as-a-service-on-boot/

import time
import os
import sys, traceback
import logging
import logging.handlers
from ConfigParser import SafeConfigParser
import socket
from threading import Thread

###########################
# PERSONAL CONFIG FILE READ
###########################

parser = SafeConfigParser()
parser.read('audioController_remoteaccess.ini')

# Read path to log file
LOG_FILENAME = parser.get('config', 'log_filename')

Socket_bind_ip_address = parser.get('config', 'socket_bind_ip_address')

Socket_bind_port = parser.getint('config', 'socket_bind_port')

Socket_max_recv_length = parser.getint('config', 'socket_max_recv_length')

#################
#  LOGGING SETUP
#################
LOG_LEVEL = logging.INFO  # Could be e.g. "DEBUG" or "WARNING"

# Configure logging to log to a file, making a new file at midnight and keeping the last 3 day's data
# Give the logger a unique name (good practice)
logger = logging.getLogger(__name__)
# Set the log level to LOG_LEVEL
logger.setLevel(LOG_LEVEL)
# Make a handler that writes to a file, making a new file at midnight and keeping 3 backups
handler = logging.handlers.TimedRotatingFileHandler(LOG_FILENAME, when="midnight", backupCount=3)
# Format each log message like this
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
# Attach the formatter to the handler
handler.setFormatter(formatter)
# Attach the handler to the logger
logger.addHandler(handler)

# Make a class we can use to capture stdout and sterr in the log
class MyLogger(object):
	def __init__(self, logger, level):
		"""Needs a logger and a logger level."""
		self.logger = logger
		self.level = level

	def write(self, message):
		# Only log if there is a message (not just a new line)
		if message.rstrip() != "":
			self.logger.log(self.level, message.rstrip())

# Replace stdout with logging to file at INFO level
sys.stdout = MyLogger(logger, logging.INFO)
# Replace stderr with logging to file at ERROR level
sys.stderr = MyLogger(logger, logging.ERROR)

logger.info('---------------------------------')
logger.info('Starting Audio controller remote access service')
logger.info('Using Socket_bind_ip_address %s' % Socket_bind_ip_address)
logger.info("Using Socket_bind_port %s" % Socket_bind_port)

def handle(clientsocket):
	while 1:
		buf = clientsocket.recv(Socket_max_recv_length)
		if buf == '': return #client terminated connection
		logger.info("Received remote command: "+ buf)

		if buf=="power_on":
			logger.info("command Power on")
			os.system('irsend simulate "0000000000061440 0 REMOTE_POWER_ON piremote"')
		elif buf=="power_off":
			logger.info("command Power off")
			os.system('irsend simulate "0000000000061441 0 REMOTE_POWER_OFF piremote"')
		else:
			logger.info("Unknown command")

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.bind((Socket_bind_ip_address, Socket_bind_port))
serversocket.listen(10)

while True:
	(clientsocket, address) = serversocket.accept()

	ct = Thread(target=handle, args=(clientsocket,))
	ct.run()
