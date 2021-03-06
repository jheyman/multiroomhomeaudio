#!/usr/bin/python

# Logging and daemon instanciatiation following this:
# 	http://blog.scphillips.com/2013/07/getting-a-python-script-to-run-in-the-background-as-a-service-on-boot/

import pylirc, time
import telnetlib
import RPi.GPIO as GPIO
import time
import smbus
import os
import sys, traceback
import logging
import logging.handlers
from ConfigParser import SafeConfigParser

###########################
# PERSONAL CONFIG FILE READ
###########################

parser = SafeConfigParser()
parser.read('audioController.ini')

# Read path to log file
LOG_FILENAME = parser.get('config', 'log_filename')

MAC_address = parser.get('config', 'mac_address')

LMS_IPaddress = parser.get('config', 'lms_ip_address')

# Get squeezelite player name from config file: it shall be equal to 
# whatever player name is specified in squeezelite startup script
PLAYER_NAME = parser.get('config', 'player_name')

# Volume to be set at server level at power on
DEFAULT_VOLUME = parser.get('config', 'default_volume')

# Gain to set on external amplifier (from 0 to 63)
AMP_GAIN = parser.getint('config', 'amp_gain')

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
logger.info('Starting Audio controller service')
logger.info('Using MAC_address %s' % MAC_address)
logger.info("Using LMS_IPaddress %s" % LMS_IPaddress)

#MAC_address = "80:1f:02:65:39:47"
#LMS_IPaddress = "192.168.0.13"

tn = telnetlib.Telnet()

def executedRemoteCommand(command):
	logger.info("Executing remote command: " + command.strip('\n'))
	tn.open(LMS_IPaddress, "9090")
	tn.write(MAC_address + command)	
	tn.close()

while(True):

	try:
		logger.info("Starting audio controller...")

		logger.info("Initializing remote control")
		if(not pylirc.init("pylirc", "./conf", 1)):
			logger.info("Error initializing pylirc")
			break	

		# Configure GPIO pin used to drive the amplifier's shutdown mode
		logger.info("Configuring GPIO")
		GPIO.setwarnings(False)	
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(23, GPIO.OUT)
		
		# check that audio amplifier is up 
		i2c_OK = False

		logger.info("Checking i2C communication...")
		GPIO.output(23, GPIO.HIGH) # make sure amp is not in shutdown mode

		while (i2c_OK == False):

			try:
				# Setup i2C communication
				bus = smbus.SMBus(1)    # use bus #1
				DEVICE_ADDRESS = 0x4b   # address of the Adafruit audio amplifier on the I2C bus
			
				# By default, set volume to 0
				bus.write_byte(DEVICE_ADDRESS, 0x00)

				i2c_OK = True
				logger.info("Audio amplifier communication is OK")

			except:
				logger.info("Error checking i2C comm, retrying...")
				time.sleep(2)
			
		GPIO.output(23, GPIO.LOW) # by default, set amp back in shutdown mode

		power=0
		muted=0

		# Verify that LMS server is up before continuing
		LMS_server_OK = False

		logger.info("Checking connection to server")
		while (LMS_server_OK == False):

			response = os.system("ping -c 1 " + LMS_IPaddress)

			if response == 0:
				logger.info("Server is up")
				LMS_server_OK = True
			else:
				logger.info("Server is not up, waiting...")
				time.sleep(2)

		logger.info("Entering main command loop...")
		while(True):

			logger.info("Waiting for next IR command...")
			s = pylirc.nextcode(1)
			if s is not None:
				cmd = s[0]["config"]
				logger.info("Command: %s", cmd)
				repeat = s[0]["repeat"]
				logger.info("Repeat: %s",repeat)
			else:
				logger.info("warning: empty code")
				continue

			if cmd == "play":
				logger.info("PLAY/PAUSE")
				executedRemoteCommand(" pause\n")
			elif (cmd == "mute"):
				logger.info("MUTE")
				executedRemoteCommand(" mixer muting\n")
				muted = not muted
			elif (cmd == "volume_plus"):
				logger.info("volume PLUS")
				executedRemoteCommand(" mixer volume +5\n")
			elif (cmd == "volume_minus"):
				logger.info("volume_minus")
				executedRemoteCommand(" mixer volume -5\n")
			elif (cmd == "previous"):
				logger.info("PREVIOUS")
				executedRemoteCommand(" playlist index -1\n")
			elif (cmd == "next"):
				logger.info("NEXT")
				executedRemoteCommand(" playlist index +1\n")
			elif (cmd == "button_1"):
				logger.info("Launching playlist_"+PLAYER_NAME+"_1.m3u")
				executedRemoteCommand(" playlist play playlist_"+PLAYER_NAME+"_1.m3u\n")
			elif (cmd == "button_2"):
				logger.info("Launching playlist_"+PLAYER_NAME+"_2.m3u")
				executedRemoteCommand(" playlist play playlist_"+PLAYER_NAME+"_2.m3u\n")
			elif (cmd == "button_3"):
				logger.info("Launching playlist_"+PLAYER_NAME+"_3.m3u")
				executedRemoteCommand(" playlist play playlist_"+PLAYER_NAME+"_3.m3u\n")
			elif (cmd == "button_4"):
				logger.info("Launching playlist_"+PLAYER_NAME+"_4.m3u")
				executedRemoteCommand(" playlist play playlist_"+PLAYER_NAME+"_4.m3u\n")
			elif (cmd == "button_5"):
				logger.info("Launching playlist_"+PLAYER_NAME+"_5.m3u")
				executedRemoteCommand(" playlist play playlist_"+PLAYER_NAME+"_5.m3u\n")
			elif (cmd == "button_6"):
				logger.info("Launching playlist_"+PLAYER_NAME+"_6.m3u")
				executedRemoteCommand(" playlist play playlist_"+PLAYER_NAME+"_6.m3u\n")
			elif (cmd == "button_7"):
				logger.info("Launching playlist_"+PLAYER_NAME+"_7.m3u")
				executedRemoteCommand(" playlist play playlist_"+PLAYER_NAME+"_7.m3u\n")
			elif (cmd == "button_8"):
				logger.info("Launching playlist_"+PLAYER_NAME+"_8.m3u")
				executedRemoteCommand(" playlist play playlist_"+PLAYER_NAME+"_8.m3u\n")
			elif (cmd == "button_9"):
				logger.info("Launching playlist_"+PLAYER_NAME+"_9.m3u")
				executedRemoteCommand(" playlist play playlist_"+PLAYER_NAME+"_9.m3u\n")
			elif (cmd == "power" or cmd == "power_on" or cmd=="power_off"):
				# Now is a good time to verify that server is still up. If it's not, go back to
				# initialization and wait for it.
				
				logger.info("[Power on/off] Checking connection to server")
				response = os.system("ping -c 1 " + LMS_IPaddress)
				if response != 0:
					logger.info("Server is down, restarting!")
					pylirc.exit()
					GPIO.cleanup()
					break

				# Handle power on/off command
				if (power == 0 or cmd=="power_on"):
					power = 1
					logger.info("power ON")

					# drive SHDN pin to HIGH to disable shutdown mode on amp, effectively turning it ON
					GPIO.output(23, GPIO.HIGH)				
					# Set amplifier to 3/4 of max gain
					bus.write_byte(DEVICE_ADDRESS, AMP_GAIN)
					time.sleep(0.5)

					# Play a locally-stored sound to notify beginning of power-up sequence
					os.system('aplay beep.wav')
					
					# Systematically restart local squeezelite player, as a workaround to squeezelite not working anymore 
					# after a a few hours (with no way to investigate why...)
					#logger.info("Restarting squeezelite server")
					#ret = os.system("sudo service squeezelite restart")
					#if response != 0:					
					#	logger.info("FAILED to restart squeezelite, ret=%d", ret)
	
					# Some time to let local squeezelite finish its restart
					#time.sleep(1)
					executedRemoteCommand(" power 1\n")				

					# Set default volume at server level
					executedRemoteCommand(" mixer volume "+DEFAULT_VOLUME+"\n")	
					
					# before loading the "on" sound, backup current playlist
					executedRemoteCommand(" playlist save tmpplaylist\n")

					# Send command to LMS to play the ON jingle to notify the successful end of power-up
					executedRemoteCommand(" playlist play audio_on.wav\n")

					# Allow for a few seconds for ON sound to be played
					time.sleep(5)

					# Restore backuped playlist
					executedRemoteCommand(" playlist resume tmpplaylist noplay:1 wipePlaylist:1\n")
				elif (power == 1 or cmd=="power_off"):
					power = 0
					logger.info("power OFF")
					os.system('aplay beep.wav')

					# before loading the "off" sound, backup current playlist
					executedRemoteCommand(" playlist save tmpplaylist\n")

					# Send command to LMS to play the OFF jingle
					executedRemoteCommand(" playlist play audio_off.wav\n")

					# Allow for a few seconds for OFF sound to be played
					time.sleep(5)

                                        #  Restore backuped playlist
                                        executedRemoteCommand(" playlist resume tmpplaylist noplay:1 wipePlaylist:1\n")

					# Set amplifier volume to zero
					bus.write_byte(DEVICE_ADDRESS, 0x00)

					# drive SHDN pin to LOW to enable shutdown mode on amp, effectively turning it OFF
					GPIO.output(23, GPIO.LOW)

					# send off command to LMS server
					executedRemoteCommand(" power 0\n")
			elif (cmd == "start_announce"):
				logger.info("START_ANNOUNCE")
				# Gcalnotifier needs access to the audio output. If audio controller is OFF, just disable shutdown mode on amp
				if power == 0:
						GPIO.output(23, GPIO.HIGH)
				## if audio controller was not already muted, mute the music
				if power == 1 and muted == 0 :
						executedRemoteCommand(" mixer muting 1\n")

			elif (cmd == "end_announce"):
				logger.info("END_ANNOUNCE")
				# Gcalnotifier releases access to the audio output. If audio controller is was OFF, re-enable shutdown mode on amp
				if power == 0:
						GPIO.output(23, GPIO.LOW)
				## if audio controller was not muted before, unmute the music now
				if power == 1 and muted == 0:
						executedRemoteCommand(" mixer muting 0\n")
			else:
				logger.info("Unknown command: "+cmd)
	except:
		logger.info("*****Exception in main loop, restarting audio controller in 5 seconds******")
		exc_type, exc_value, exc_traceback = sys.exc_info()
		traceback.print_exception(exc_type, exc_value, exc_traceback,limit=2, file=sys.stdout)	
		del exc_traceback
		pylirc.exit()
		GPIO.cleanup()
		time.sleep(5.0)
		continue
