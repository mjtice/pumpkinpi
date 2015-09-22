#!/usr/bin/env python2.7
# script by Alex Eames http://RasPi.tv
#http://RasPi.tv/2013/how-to-use-soft-pwm-in-rpi-gpio-pt-2-led-dimming-and-motor-speed-control
# Using PWM with RPi.GPIO pt 2 - requires RPi.GPIO 0.5.2a or higher

import RPi.GPIO as GPIO
from time import sleep
from ISStreamer.Streamer import Streamer

## Streamer constructor, this will create a bucket called Double Button LED
## you'll be able to see this name in your list of logs on initialstate.com
## your access_key is a secret and is specific to you, don't share it!
streamer = Streamer(bucket_name="Pumpkin", access_key="h1vnHLHbx2qNOxISbkKStbaXDx89k6Ya")

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM) ## Indicates which pin numbering configuration to use

GPIO.setup(17, GPIO.OUT)
GPIO.setup(18, GPIO.OUT)
GPIO.setup(23, GPIO.IN, GPIO.PUD_UP)

led = GPIO.PWM(18, 100)

led.start(0)         
pause_time = 0.01
state = 1

try:
    while True:
        if (state == 1):
            streamer.log("state", state)
            GPIO.output(17,GPIO.HIGH)
            state = 0
        else:
            streamer.log("state", state)
            GPIO.output(17,GPIO.LOW)
            state = 1
             
        ## When state toggle button is pressed
        if ( GPIO.input(23) == True ):
            streamer.log("button", "pressed")
            GPIO.output(17,GPIO.HIGH)
            for x in range(0,3):
                for i in range(0,101):      # 101 because it stops when it finishes 100
                    led.ChangeDutyCycle(i)
                    sleep(pause_time)
                for i in range(100,-1,-1):      # from 100 to zero in steps of -1
                    led.ChangeDutyCycle(i)
                    sleep(pause_time)

            sleep(2)
            streamer.log("horn", "blast")
            print("honk")

        sleep(.3)

except KeyboardInterrupt:
    led.stop()
    GPIO.cleanup()
    streamer.close()
