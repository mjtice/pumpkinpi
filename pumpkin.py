import RPi.GPIO as GPIO
from time import sleep
import random
import threading
import math
import logging
import sys


class Pumpkin(object):
    def __init__(self):
        # setup logging
        self.log = logging.getLogger()
        self.log.setLevel(logging.DEBUG)

        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.log.addHandler(handler)

        # Initialize all the GPIO pins
        self.gpio_pins = {
            "eye_left": 27,
            "eye_right": 22,
            "nose": 23,
            "mouth": 24,
            "horn": 25,
            "candle_red": 19,
            "candle_green": 26
        }
        for i in self.gpio_pins.items():
            self.log.debug("{} is assigned pin {}".format(i[0], i[1]))

        self.log.debug("GPIO pins assigned, setting up GPIO.")

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)  ## Indicates which pin numbering configuration to use

        GPIO.setup(self.gpio_pins['eye_left'], GPIO.OUT)
        GPIO.setup(self.gpio_pins['eye_right'], GPIO.OUT)
        GPIO.setup(self.gpio_pins['nose'], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.gpio_pins['mouth'], GPIO.OUT)
        GPIO.setup(self.gpio_pins['horn'], GPIO.OUT)
        GPIO.setup(self.gpio_pins['candle_red'], GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.gpio_pins['candle_green'], GPIO.OUT, initial=GPIO.LOW)

        self.log.debug("GPIO setup.  Setting OUTPUT for horn, mouth, eye_left, eye_right")
        GPIO.output(self.gpio_pins['horn'], GPIO.LOW)
        GPIO.output(self.gpio_pins['mouth'], GPIO.HIGH)
        GPIO.output(self.gpio_pins['eye_left'], GPIO.HIGH)
        GPIO.output(self.gpio_pins['eye_right'], GPIO.HIGH)

        self.log.debug("Enabling PWM on mouth, candle_red, candle_green")
        self.pwm_mouth = GPIO.PWM(self.gpio_pins['mouth'], 100)
        self.pwm_candle_red = GPIO.PWM(self.gpio_pins['candle_red'], 300)
        self.pwm_candle_green = GPIO.PWM(self.gpio_pins['candle_green'], 300)
        self.intensity = 1.0

        self.pwm = [self.pwm_mouth, self.pwm_candle_red, self.pwm_candle_green]

        # Start the pins
        self.log.debug("Starting PWM on mouth, candle_red, candle_green")
        self.pwm_mouth.start(0)
        self.pwm_candle_red.start(100)
        self.pwm_candle_green.start(100)

        threads = [
            threading.Thread(target=self._red_light, args=(self.pwm_candle_red, self.intensity)),
            threading.Thread(target=self._green_light, args=(self.pwm_candle_red, self.intensity)),
        ]

        for t in threads:
            self.log.debug("Starting thread...")
            t.daemon = True
            t.start()
            self.log.debug("Thread started")
        # for t in threads:
        #     self.log.debug("Joining threads...")
        #     t.join()
        #     self.log.debug("Thread joined")

    def _red_light(self, candle, intensity):
        self.log.debug("Starting red_candle thread")
        candle.start(100)
        while True:
            candle.ChangeDutyCycle(min(random.randint(75, 100) * math.pow(intensity + 0.1, 0.75), 100))
            self._rand_flicker_sleep()

    def _green_light(self, candle, intensity):
        self.log.debug("Starting green_candle thread")
        candle.start(100)
        while True:
            candle.ChangeDutyCycle(random.randint(33, 44) * math.pow(intensity, 2))
            self._rand_flicker_sleep()

    def burning_down(self):
        self.log.debug("Starting candle burn down")
        while self.intensity > 0:
            self.intensity = max(self.intensity - .01, 0)
            self.pwm_candle_red.ChangeDutyCycle(self.intensity)
            self.pwm_candle_green.ChangeDutyCycle(self.intensity)
            sleep(.05)
        self.intensity = 1.0
        self.log.debug("Candle burn down complete")

    def mouth(self):
        self.log.debug("Starting mouth cycle")
        pause_time = 0.02

        for i in range(0, 101):  # 101 because it stops when it finishes 100
            self.pwm_mouth.ChangeDutyCycle(i)
            sleep(pause_time)
        for i in range(100, -1, -1):  # from 100 to zero in steps of -1
            self.pwm_mouth.ChangeDutyCycle(i)
            sleep(pause_time)
        self.log.debug("Mouth cycle complete")

    def horn(self):
        self.log.debug("Starting horn cycle")

        sleep(2)
        GPIO.output(self.gpio_pins['horn'], GPIO.HIGH)
        sleep(.3)
        GPIO.output(self.gpio_pins['horn'], GPIO.LOW)
        self.log.debug("Horn cycle complete")

    def _rand_flicker_sleep(self):
        sleep(random.randint(3, 10) / 100.0)

    def blink(self):
        self.log.debug("Starting blink cycle")
        random_number = random.uniform(.1, .3)
        GPIO.output(self.gpio_pins['eye_left'], GPIO.LOW)
        GPIO.output(self.gpio_pins['eye_right'], GPIO.LOW)

        sleep(random_number)
        GPIO.output(self.gpio_pins['eye_left'], GPIO.HIGH)
        GPIO.output(self.gpio_pins['eye_right'], GPIO.HIGH)

        random_int = random.uniform(1, 10)
        if random_int >= 6:
            random_number = random.uniform(.1, .2)
            GPIO.output(self.gpio_pins['eye_left'], GPIO.LOW)
            GPIO.output(self.gpio_pins['eye_right'], GPIO.LOW)

            sleep(random_number)
            GPIO.output(self.gpio_pins['eye_left'], GPIO.HIGH)
            GPIO.output(self.gpio_pins['eye_right'], GPIO.HIGH)
        self.log.debug("Blink cycle complete")


def main():
    pumpkin = None
    try:
        # Blink Rate http://www.ncbi.nlm.nih.gov/pubmed/9399231
        # Blink once every 3.5 seconds (more or less)
        blink_rate = 3.529

        counter = 0
        pumpkin = Pumpkin()

        while True:
            if counter >= blink_rate:
                random_number = random.uniform(0, .2)
                sleep(random_number)
                pumpkin.blink()
                counter = 0

            # When state toggle button is pressed
            if GPIO.input(pumpkin.gpio_pins['nose']) == GPIO.HIGH:
                pumpkin.log.debug("Nose was pushed...")
                # Turn the eyes on
                GPIO.output(pumpkin.gpio_pins['eye_left'], GPIO.HIGH)
                GPIO.output(pumpkin.gpio_pins['eye_right'], GPIO.HIGH)

                # Dim the candle
                pumpkin.burning_down()

                # Cycle mouth
                pumpkin.mouth()
                sleep(2)

                # Honk the horn
                pumpkin.horn()
            counter = counter + .001

            # Artificial sleep to capture the button
            sleep(.001)

    except KeyboardInterrupt:
        pass
    except SystemExit:
        pass
    finally:
        for p in pumpkin.pwm:
            p.stop()
        GPIO.cleanup()


if __name__ == '__main__':
    main()
