#!/usr/bin/env python2.7

import RPi.GPIO as GPIO
from time import sleep
from ISStreamer.Streamer import Streamer

## Streamer constructor, this will create a bucket called Double Button LED
## you'll be able to see this name in your list of logs on initialstate.com
## your access_key is a secret and is specific to you, don't share it!
streamer = Streamer(bucket_name="", access_key="")

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM) ## Indicates which pin numbering configuration to use

ledEye = 17
ledMouth = 18
btnNose = 23

GPIO.setup(ledMouth, GPIO.OUT)
GPIO.setup(ledEye, GPIO.OUT)
GPIO.setup(btnNose, GPIO.IN, GPIO.PUD_UP)

led = GPIO.PWM(ledMouth, 100)

led.start(0)         
pause_time = 0.02
state = 1

# Blink Rate http://www.ncbi.nlm.nih.gov/pubmed/9399231
# Blink once every 3.5 seconds
blinkRate = 3.529
counter = 0
GPIO.output(ledEye,GPIO.HIGH)

try:
    while True:
        if (counter >= blinkRate):
            streamer.log("state", state)
            GPIO.output(ledEye,GPIO.LOW)
            sleep(.1)
            GPIO.output(ledEye,GPIO.HIGH)
            counter = 0
        
        ## When state toggle button is pressed
        if ( GPIO.input(btnNose) == True ):
            streamer.log("button", "pressed")
            GPIO.output(ledEye,GPIO.HIGH)
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
        
        counter = counter + .001
        sleep(.001)

except KeyboardInterrupt:
    led.stop()
    GPIO.cleanup()
    streamer.close()
