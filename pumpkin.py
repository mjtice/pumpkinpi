#!/usr/bin/env python2.7

import RPi.GPIO as GPIO
import signal
from time import sleep
import random

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM) ## Indicates which pin numbering configuration to use

ledEye = [27,22]
btnNose = 23
ledMouth = 24
horn = 25

GPIO.setup(ledMouth, GPIO.OUT)
GPIO.output(ledMouth,GPIO.HIGH)
GPIO.setup(ledEye, GPIO.OUT)
GPIO.setup(btnNose, GPIO.IN, GPIO.PUD_UP)
GPIO.setup(horn, GPIO.OUT)
GPIO.output(horn,GPIO.HIGH)

led = GPIO.PWM(ledMouth, 100)

led.start(0)         
pause_time = 0.02
state = 1

# Blink Rate http://www.ncbi.nlm.nih.gov/pubmed/9399231
# Blink once every 3.5 seconds (more or less)
blinkRate = 3.529
counter = 0
GPIO.output(ledEye,GPIO.HIGH)

def signal_term_handler(signal, frame):
    GPIO.cleanup()

def blink():
    randomNumber = random.uniform(.1,.3)
    GPIO.output(ledEye,GPIO.LOW)
    sleep(randomNumber)
    GPIO.output(ledEye,GPIO.HIGH)

    randomInt = random.uniform(1, 10)
    if (randomInt >= 6):
        randomNumber = random.uniform(.1,.2)
        GPIO.output(ledEye,GPIO.LOW)
        sleep(randomNumber)
        GPIO.output(ledEye,GPIO.HIGH)

try:
    while True:
        if (counter >= blinkRate):
            randomNumber = random.uniform(0,.2)
            sleep(randomNumber)
            blink()
            counter = 0

        ## When state toggle button is pressed
        if ( GPIO.input(btnNose) == False ):
            GPIO.output(ledEye,GPIO.HIGH)
            for x in range(0,1):
                for i in range(0,101):      # 101 because it stops when it finishes 100
                    led.ChangeDutyCycle(i)
                    sleep(pause_time)
                    print(i)
                for i in range(100,-1,-1):      # from 100 to zero in steps of -1
                    led.ChangeDutyCycle(i)
                    sleep(pause_time)
                    print(i)

            sleep(2)
            GPIO.output(horn,GPIO.LOW)
            print "Honk!"
            sleep(.3)
            GPIO.output(horn,GPIO.HIGH)
        
        counter = counter + .001
        signal.signal(signal.SIGTERM, signal_term_handler)
        sleep(.001)

except KeyboardInterrupt:
    led.stop()
    GPIO.cleanup()
    #streamer.close()

except SystemExit:
    led.stop()
    GPIO.cleanup()
