import RPi.GPIO as GPIO
import time

OUTLETS = [23]

class GPIOcontrol:
    def __init__(self):
        GPIO.setmode(GPIO.BCM) #set numbering scheme to GPIO numbers
        GPIO.setup(OUTLETS[0], GPIO.OUT) #set GPIO on pi to outputs

        GPIO.output(OUTLETS[0], True) #when initialized, set high so power is not applied
        
    def control(self, outlet, on):
        if outlet <= len(OUTLETS):
            GPIO.output(OUTLETS[outlet - 1], not on)