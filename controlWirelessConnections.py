#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# controlWiFiButton.py python module
# python script to control the wireless connections (WiFi/Bluetooth)
#  on the push of a button
#
# Author: Solveigh
#
# required: sudo apt-get install python-dev python-rpi.gpio
#
# requires files raspi-blacklist.conf_Wireless and raspi-blacklist.conf_noWireless in /etc/modprobe.d
# run: sudo python controlWirelessConnections.py

import sys
import time
from time import sleep
import RPi.GPIO as GPIO
import os

GPIN=21
GPIO.setmode(GPIO.BCM)

# Pin 21 will be input and will have its pull-up resistor (to 3V3) activated
# so we only need to connect a push button with a current limiting resistor to ground
GPIO.setup(GPIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
int_active = 0

# ISR: if our button is pressed, we will have a falling edge on pin 21
# this will trigger this interrupt:
def Int_wlancontrol(channel):

  # button is pressed
  # possibly shutdown our Raspberry Pi

  global int_active

  # only react when there is no other shutdown process running

  if (int_active == 0):
    int_active = 1
    pressed = 1
    shutdown = 0

    # count how long the button is pressed
    counter = 0

    while ( pressed == 1 ):
      if ( GPIO.input(GPIN) == False ):
        # button is still pressed
        counter = counter + 1
        print('pressed: ' + str(counter))
        # break if we count beyond 20 (long-press is a shutdown)
        if (counter >= 20):
          pressed = 0
        else:
          sleep(0.2)
      else:
        # button has been released
        pressed = 0

        # button has been released, count cycles and determine action

        # count how long the button was pressed
        if (counter < 2):
          # short press, do nothing
          pressed = 0
          int_active = 0
          print('Short press, do nothing')
        else:
          # longer press
          if (counter < 10):

            # medium length press, initiate system reboot

            print('Medium length press.')
            print('Turn off wireless connections.')
            #os.system("sudo ifconfig wlan0 down --force")

            # soft block wifi/bluetooth
            #os.system("sudo rfkill block wifi")
            #os.system("sudo rfkill block bluetooth")

            # unload drivers and reboot
            os.system('sudo cp /etc/modprobe.d/raspi-blacklist.conf_noWireless /etc/modprobe.d/raspi-blacklist.conf')
            os.system('sudo reboot now')

            time.sleep(3)
            #os.system("rfkill list > res_down.txt")
            counter = 0
            pressed = 0
            int_active = 0
          elif (counter>=10 and counter<20):
            # long press, initiate system shutdown

            print('Long press.')
            print('Turn on wireless connections.')
            #os.system("sudo ifconfig wlan0 up --force")
            # soft unblock wifi/bluetooth
            #os.system("sudo rfkill unblock wifi")
            #os.system("sudo rfkill unblock bluetooth")

            # load drivers and reboot
            os.system('sudo cp /etc/modprobe.d/raspi-blacklist.conf_Wireless /etc/modprobe.d/raspi-blacklist.conf')
            os.system('sudo reboot now')

            counter = 0
            pressed = 0
            int_active = 0

# Now we are programming pin 21 as an interrupt input
# it will react on a falling edge and call our interrupt routine "Int_shutdown"
GPIO.add_event_detect(GPIN, GPIO.FALLING,  callback = Int_wlancontrol, bouncetime = 500)

while True:
  print('.')
  time.sleep(1)
