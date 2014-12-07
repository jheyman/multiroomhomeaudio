#!/usr/bin/python
import pylirc, time
import telnetlib
import RPi.GPIO as GPIO
import time
import smbus
import os

MAC_address = "80:1f:02:65:39:47"
LMS_IPaddress = "192.168.0.13"

tn = telnetlib.Telnet()

while(True):
	
	print "Starting audio controller..."

	print "Initializing remote control"
	if(not pylirc.init("pylirc", "./conf", 1)):
		print "Error initializing pylirc"
		break	

	# Configure GPIO pin used to drive the amplifier's shutdown mode
	print "Configuring GPIO"
	GPIO.setwarnings(False)	
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(23, GPIO.OUT)
	
	# check that audio amplifier is up 
	i2c_OK = False

	print "Checking  i2C communication..."
	GPIO.output(23, GPIO.HIGH) # make sure amp is not in shutdown mode

	while (i2c_OK == False):

		try:
			# Setup i2C communication
			bus = smbus.SMBus(1)    # use bus #1
			DEVICE_ADDRESS = 0x4b   # address of the Adafruit audio amplifier on the I2C bus
		
			# By default, set volume to 0
			bus.write_byte(DEVICE_ADDRESS, 0x00)

			i2c_OK = True
			print "Audio amplifier communication is OK"

		except:
			print "Error checking i2C comm, retrying..."
			time.sleep(2)
		
	GPIO.output(23, GPIO.LOW) # by default, set amp back in shutdown mode

	power=0

	# Verify that LMS server is up before continuing
	LMS_server_OK = False

	print "Checking connection to server"
	while (LMS_server_OK == False):

		response = os.system("ping -c 1 " + LMS_IPaddress)

		if response == 0:
			print "Server is up"
			LMS_server_OK = True
		else:
			print "Server is not up, waiting..."
			time.sleep(2)

	try:
		print "Entering main command loop..."
		while(True):
			print "Waiting for next IR command..."
			s = pylirc.nextcode(1)
			if s is not None:
				cmd = s[0]["config"]
				print "Command: %s" % cmd
				repeat = s[0]["repeat"]
				print "Repeat: %s" % repeat
			else:
				continue

			if cmd == "play":
				print "PLAY/PAUSE"
				tn.write(MAC_address + " pause\n")
			elif (cmd == "mute"):
				print "MUTE"
				tn.write(MAC_address + " mixer muting\n")
			elif (cmd == "volume_plus"):
				print "volume PLUS"
				tn.write(MAC_address + " mixer volume +5\n")
			elif (cmd == "volume_minus"):
				print "volume_minus"
				tn.write(MAC_address + " mixer volume -5\n")
			elif (cmd == "previous"):
				print "PREVIOUS"
				tn.write(MAC_address + " playlist index -1\n")
			elif (cmd == "next"):
				print "NEXT"
				tn.write(MAC_address + " playlist index +1\n")
			elif (cmd == "button_1"):
				print "PLAYLIST_1"
				tn.write(MAC_address + " playlist play playlist_1.m3u\n")
			elif (cmd == "button_2"):
				print "PLAYLIST_2"
				tn.write(MAC_address + " playlist play playlist_2.m3u\n")
			elif (cmd == "button_3"):
				print "PLAYLIST_3"
				tn.write(MAC_address + " playlist play playlist_3.m3u\n")
			elif (cmd == "button_4"):
				print "PLAYLIST_4"
				tn.write(MAC_address + " playlist play playlist_4.m3u\n")
			elif (cmd == "button_5"):
				print "PLAYLIST_5"
				tn.write(MAC_address + " playlist play playlist_5.m3u\n")
			elif (cmd == "button_6"):
				print "PLAYLIST_6"
				tn.write(MAC_address + " playlist play playlist_6.m3u\n")
			elif (cmd == "button_7"):
				print "PLAYLIST_7"
				tn.write(MAC_address + " playlist play playlist_7.m3u\n")
			elif (cmd == "button_8"):
				print "PLAYLIST_8"
				tn.write(MAC_address + " playlist play playlist_8.m3u\n")
			elif (cmd == "button_9"):
				print "PLAYLIST_9"
				tn.write(MAC_address + " playlist play playlist_9.m3u\n")
			elif (cmd == "power"):
				# Now is a good time to verify that server is still up. If it's not, go back to
				# initialization and wait for it.
				print "[Power onf/off] Checking connection to server"
				response = os.system("ping -c 1 " + LMS_IPaddress)
				if response != 0:
					print "Server is down, restarting!"
					pylirc.exit()
					GPIO.cleanup()
					break

				# Handle power on/off command
				if (power == 0):
					power = 1
					print "power ON"
					print "Initializing telnet connection to server"
					if (tn is not None):
						tn.open(LMS_IPaddress, "9090")					
					# drive SHDN pin to HIGH to disable shutdown mode on amp, effectively turning it ON
					GPIO.output(23, GPIO.HIGH)
					# Set amplifier to max 3/4 of max gain
					bus.write_byte(DEVICE_ADDRESS, 0x30)
					# Send command to LMS to play the ON jingle
					tn.write(MAC_address + " playlist play audio_on.wav\n")
				elif (power == 1):
					power = 0
					print "power OFF"
					# Send command to LMS to play the OFF jingle
					tn.write(MAC_address + " playlist play audio_off.wav\n")
					# Allow for a few seconds for OFF sound to be played
					time.sleep(5)
					# Set amplifier volume to zero
					bus.write_byte(DEVICE_ADDRESS, 0x00)
					# drive SHDN pin to LOW to enable shutdown mode on amp, effectively turning it OFF
					GPIO.output(23, GPIO.LOW)

					if (tn is not None):
						tn.close()
	except:
		print "Exception in main loop, restarting audio controller"
		continue


   
