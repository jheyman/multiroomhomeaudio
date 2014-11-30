#!/usr/bin/python
import pylirc, time
import telnetlib


MAC_address = "80:1f:02:65:39:47"
power=0

tn = telnetlib.Telnet("192.168.0.13", "9090")
if(pylirc.init("pylirc", "./conf", 1)):

   while(True):
      s = pylirc.nextcode(1)
      if s is not None:
         cmd = s[0]["config"]
         print "Command: %s" % cmd
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
            if (power == 0):
               power = 1
               print "power ON"
               tn.write(MAC_address + " playlist play audio_on.wav\n")
            elif (power == 1):
               power = 0
               print "power OFF"
               tn.write(MAC_address + " playlist play audio_off.wav\n")
          

   # Clean up lirc
   pylirc.exit()

   
