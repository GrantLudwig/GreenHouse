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

    def __readJson(self):
        with open("files/variables.json", "r") as json_data:
            self.__variablesJson = json.load(json_data)

        self.__plantName = self.__plantJson["Name"]
        self.__waterLeft = self.__plantJson["CurrWater"]
        self.__plantTime = self.__plantJson["PlantTime"]

    def __writeJson(self):
        with open("files/plantInfo.json", 'w') as outfile:
            json.dump(self.__plantJson, outfile)

    def stop(self):
        self.__running = False
        self.__relayControl.control(1, False)  # Turn off pump
        self.__relayControl.control(2, False)  # Turn off pump

    def __sensorMeasurements(self):
        print("Sensors Being Measured")

        # ---- Temperature ----
        self.__lastTempMeasure = self.__temp.read_temp()

        # ---- Moisture ----
        self.__lastMoistureMeasure = self.__moisture.get_moisture()
        if self.__lastMoistureMeasure <= self.SOIL_MOISTURE_LEVEL:
            if self.__firstMoistureFail and not self.__wateredLastRound:
                self.__watering()
                self.__firstMoistureFail = False
                self.__wateredLastRound = True
            else:
                self.__firstMoistureFail = True
                self.__wateredLastRound = False
        else:
            self.__wateredLastRound = False
            self.__firstMoistureFail = False

        # ---- Lighting ---- FIXME

        currentDT = datetime.datetime.now()
        self.__lastSpectrumMeasure, self.__lastIrMeasure = self.__light.get_full_luminosity()
        if currentDT.hour >= self.DAYLIGHT and currentDT.hour < self.LIGHTING_TIME:
            if not self.__nightLightOn:  # check if light was still on
                self.__nightLightOn = False
                self.__aggregateSpectrum = 0
                self.__aggregateIr = 0
                self.__nightTime = self.HOURS_OF_LIGHT_ON * 60  # hours to min
            self.__aggregateSpectrum += self.__lastSpectrumMeasure
            self.__aggregateIr += self.__lastIrMeasure
        elif self.__aggregateSpectrum < self.ENOUGH_SPECTRUM or self.__aggregateIr < self.ENOUGH_IR:
            self.__aggregateSpectrum += self.__lastSpectrumMeasure
            self.__aggregateIr += self.__lastIrMeasure

            if not self.__nightLightOn:
                self.__nightLightOn = True
                self.__prevNightTime = self.__nightTime
                self.__lightOnTime = time.time()

            if self.__aggregateSpectrum >= self.ENOUGH_SPECTRUM and self.__aggregateIr >= self.ENOUGH_IR:
                self.__nightLightOn = False

        else:
            self.__nightLightOn = False
            self.__aggregateSpectrum = 0
            self.__aggregateIr = 0
            self.__nightTime = time.time() - self.__lightOnTime / 60  # seconds to min

        # turn on and off light
        if self.__nightLightOn:
            self.__relayControl.control(self.LIGHT_OUTLET, True)
        else:
            self.__relayControl.control(self.LIGHT_OUTLET, False)

        self.__printSensorMeasures()

    def run(self):
        while self.__running:
            if self.__lastLoopTime + self.SENSOR_MEASURE_INTERVAL <= time.time():
                self.__sensorMeasurements()
                self.__lastLoopTime = time.time()
            time.sleep(5)