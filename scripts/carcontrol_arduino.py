#!/usr/bin/env python3

"""
Helper used to handle actions based on serial communication with an Arduino with
a Sparkfun Qwiic Twist rotary encoder/switch.
Data is sent as JSON stanzas over serial.

Some of the code is derived from: https://gist.github.com/savetheclocktower/9b5f67c20f6c04e65ed88f2e594d43c1
"""

import os
import signal
import subprocess
import sys
import threading
import queue
import serial
import json
import rpi_backlight as bl

# Conf variables
SERIAL_PORT = "/dev/ttyUSB0"
SERIAL_RATE = 9600
CTL_PORT = 8888
MIXER_CARD = 0
MIXER_CHANNEL = "Digital"
VOL_MIN = 0
VOL_MAX = 100
VOL_INC = 1
BRIGHTNESS_MIN = 11
BRIGHTNESS_MAX = 255
BRIGHTNESS_INC = 25

# Button modes
MODE_VOL = 1
MODE_BRI = 2
MODE_CAM = 3

# Create a queue to manage incoming serial data and an event to signal the main
# thread that new data is available
serial_queue = queue.Queue()
queue_event = threading.Event()

class VolumeError(Exception):
    pass

class Volume:
    """
    Wrapper class to handle volume operations using amixer
    """

    MIN = VOL_MIN
    MAX = VOL_MAX
    INC = VOL_INC
    CHAN = MIXER_CHANNEL

    def __init__(self):
        self.last_volume = self.MIN
        self._sync()
    
    def increase(self):
        """
        Increase the volume by one increment
        """
        return self.change(self.INC)

    def lower(self):
        """
        Lower the volume by one increment
        """
        return self.change(-self.INC)

    def change(self, delta):
        v = self.volume + delta
        v = self._constrain(v)

        return self.set_volume(v)

    def set_volume(self, v):
        """
        Set the volume to a specific value
        """
        self.volume = self._constrain(v)
        output = self.amixer("set '{}' unmute {}%".format(self.CHAN, v))
        self._sync(output)

        return self.volume

    def toggle(self):
        """
        Toggle muting on and off
        """
        if self.is_muted:
            output = self.amixer("set '{}' unmute".format(self.CHAN))
        else:
            self.last_volume = self.volume
            output = self.amixer("set '{}' mute".format(self.CHAN))

        self._sync(output)

        if not self.is_muted:
            self.set_volume(self.last_volume)

        return self.is_muted

    def status(self):
        if self.is_muted:
            return "{}% (muted)".format(self.volume)

        return "{}%".format(self.volume)

    def _sync(self, output=None):
        if output is None:
            output = self.amixer("get '{}'".format(self.CHAN))

        lines = output.readlines()
        last = lines[-1].decode('utf-8')

        # The last line of output will have two values in square brackets. The
        # first will be the volume (e.g., "[95%]") and the second will be the
        # mute state ("[off]" or "[on]").
        i1 = last.rindex('[') + 1
        i2 = last.rindex(']')

        self.is_muted = last[i1:i2] == 'off'

        i1 = last.index('[') + 1
        i2 = last.index('%')
        pct = last[i1:i2]

        self.volume = int(pct)

    def _constrain(self,v):
        if v < self.MIN:
            return self.MIN

        if v > self.MAX:
            return self.MAX

        return v

    def amixer(self, cmd):
        #p = subprocess.Popen("amixer {}".format(cmd), shell=True, stdout=subprocess.PIPE, env=os.environ.copy())
        p = subprocess.Popen("amixer -c{} {}".format(MIXER_CARD, cmd), shell=True, stdout=subprocess.PIPE, env=os.environ.copy())
        code = p.wait()
        if code != 0:
            raise VolumeError("Unknown error")
            sys.exit(0)

        return p.stdout

def serial_loop(queue):
    buff = bytearray()
    serial_port = serial.Serial(SERIAL_PORT, SERIAL_RATE, timeout=0)
    while (serial_port.is_open):
        i = buff.find(b"\n")
        if i >= 0:
            r = buff[:i+1]
            buff = buff[i+1:]
            queue.put(r)
            queue_event.set()
        while True:
            i = max(1, min(2048, serial_port.in_waiting))
            data = serial_port.read(1)
            i = data.find(b"\n")
            if i >= 0:
                r = buff + data[:i+1]
                buff[0:] = data[i+1:]
                queue.put(r)
                queue_event.set()
            else:
                buff.extend(data)
        line = serial_port.readline()
        if line:
            queue.put(line)
            queue_event.set()

def increaseBrightness(inc):
    current = bl.get_actual_brightness()
    target = current + (25*inc)
    if current < 255:
        if target > 255:
            target = 255
        bl.set_brightness(target, smooth=False)

def decreaseBrightness(inc):
    current = bl.get_actual_brightness()
    target = current + (25*inc)
    if current > 11:
        if target < 11:
            target = 11
        bl.set_brightness(target, smooth=False)


def startCamera():
    global is_cam_running
    global player_process
    if is_cam_running is False:
        try:
            print("Switching camera On")
            #self.stream_process = subprocess.Popen(self.stream_cmd, shell=True, preexec_fn=os.setsid)
            #print "Stream launched"
            #time.sleep(0.5)
            player_process = subprocess.Popen(player_cmd, shell=True, preexec_fn=os.setsid)
            print("Player launched")
            is_cam_running = True
        except:
            pass

    return is_cam_running

def stopCamera():
    global is_cam_running
    global player_process
    if is_cam_running:
        try:
            os.killpg(os.getpgid(player_process.pid), signal.SIGKILL)
            #time.sleep(0.5)
            #os.killpg(os.getpgid(self.stream_process.pid), signal.SIGKILL)
            is_cam_running = False
            print("Stopping camera")
        except:
            pass

    return is_cam_running

if __name__ == "__main__":
    try:
        is_cam_running = False
        player_process = 0
        player_cmd = "cd /home/pi/src/cam_overlay/; ./cam_overlay.bin"

        serial_thread = threading.Thread(target=serial_loop, args=(serial_queue,), daemon=True)
        serial_thread.start()

        vol = Volume()


        def process_event(payload):
            global is_cam_running
            stanza = json.loads(payload)

            if stanza:
                if 'mode' in stanza:
                    if stanza['mode'] == MODE_VOL:
                        is_cam_running = stopCamera()
                        if 'diff' in stanza and stanza['diff'] is not 0:
                            vol.change(stanza['diff'])
                    elif stanza['mode'] == MODE_BRI:
                        is_cam_running = stopCamera()
                        if 'diff' in stanza and stanza['diff'] is not 0:
                            if stanza['diff'] > 0:
                                increaseBrightness(stanza['diff'])
                            else:
                                decreaseBrightness(stanza['diff'])
                    elif stanza['mode'] == MODE_CAM:
                        is_cam_running = startCamera()


        def consume_queue():
            while not serial_queue.empty():
                process_event(serial_queue.get().decode('utf-8'))

        while True:
            queue_event.wait(1200)
            consume_queue()
            queue_event.clear()

    except KeyboardInterrupt:
        raise
        sys.exit(0)
    except:
        raise
        sys.exit(0)
