#!/usr/bin/python3
# Monitors events (temperature, inputs, ...) to trigger actions

import sys
import os
import time
import RPi.GPIO as GPIO
from pijuice import PiJuice

# Check for python3 (pijuice >= 1.4 requires Python3)
if sys.version_info < (3, 0):
    sys.stfout.write("This script requires Python 3.x to work.")
    sys.exti(1)

# Configuration
FAN_PIN = 25
BAT_HIGH_TEMP = 35
BAT_DIFF_TEMP = 3
CPU_HIGH_TEMP = 60
CPU_TEMP_DIFF = 5
#cam_pin = 0 TODO

# Vars
debug = False
bat_temp = 0
cpu_temp = 0
is_fan_on = False

# Setup
pijuice = PiJuice(1,0x14)
GPIO.setmode(GPIO.BCM)
GPIO.setup(FAN_PIN, GPIO.OUT, initial=GPIO.LOW)

if len(sys.argv) > 1 and sys.argv[1] == 'debug':
    debug = True

while True:
    try:
        # Get bat temp
        bat_temp = pijuice.status.GetBatteryTemperature()['data']
        # Get cpu temp
        cpu_temp = float(os.popen("vcgencmd measure_temp").readline().rstrip().replace("temp=","").replace("'C",""))

        if debug:
            print("BAT temp is: " + str(bat_temp) + "C")
            print("CPU temp is: " + str(cpu_temp) + "C")

        if bat_temp >= BAT_HIGH_TEMP or cpu_temp >= CPU_HIGH_TEMP:
            # Turn fan on/keep fan on
            if is_fan_on is False:
                is_fan_on = True
                GPIO.output(FAN_PIN, GPIO.HIGH)
                if debug:
                    print("Turning fan ON")
        else:
            if is_fan_on and (bat_temp <= (BAT_HIGH_TEMP - BAT_DIFF_TEMP) and cpu_temp <= (CPU_HIGH_TEMP - CPU_TEMP_DIFF)):
                # Safe temp reached, turn fan off
                GPIO.output(FAN_PIN, GPIO.LOW)
                is_fan_on = False
                if debug:
                    print("Turning fan OFF")
        time.sleep(1)
    except KeyboardInterrupt:
        GPIO.cleanup()
        sys.exit(0)
    except:
        pass
