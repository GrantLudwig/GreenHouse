import time
import threading
import json
from relay_control import GPIOcontrol as RelayControl
import RPi.GPIO as GPIO

class Sensors(threading.Thread):

    SENSOR_MEASURE_INTERVAL = 600  # seconds, 10 min

    def __init__(self):
        threading.Thread.__init__(self)
        GPIO.setwarnings(False)

        self.__lastLoopTime = 0
        self.__variablesJson = None
        self.__readJson()

        self.waterDuration = None
        self.timeBetweenWatering = None
        self.waterStartTime = None
        self.waterEndTime = None
        self.lastWater = None

    def __readJson(self):
        with open("files/variables.json", "r") as json_data:
            self.__variablesJson = json.load(json_data)

        self.waterDuration = self.__variablesJson["WaterDuration"]
        self.timeBetweenWatering = self.__variablesJson["TimeBetweenWatering"]
        self.waterStartTime = self.__variablesJson["WaterStartTime"]
        self.waterEndTime = self.__variablesJson["WaterEndTime"]
        self.lastWater = self.__variablesJson["LastWater"]

    def __writeJson(self):
        with open("files/variables.json", 'w') as outfile:
            json.dump(self.__variablesJson, outfile)

    def stop(self):
        self.__running = False
        self.__relayControl.control(1, False)  # Turn off pump
        self.__relayControl.control(2, False)  # Turn off pump

    def __sensorMeasurements(self):
        print("Sensors Being Measured")

        self.__printSensorMeasures()

    def run(self):
        while self.__running:
            if self.__lastLoopTime + self.SENSOR_MEASURE_INTERVAL <= time.time():
                self.__sensorMeasurements()
                self.__lastLoopTime = time.time()
            time.sleep(5)