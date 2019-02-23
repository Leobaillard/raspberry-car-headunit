#!/usr/bin/python
# Executes actions based on inputs from IR remote and GPIO

import sys
import time
import socket
import uinput
import subprocess, os
import signal
import rpi_backlight as bl

class IrCtl:
    def __init__(self):
        # Init virtual keyboard
        self.kbd = uinput.Device([
            uinput.KEY_B,
            uinput.KEY_H,
            uinput.KEY_M,
            uinput.KEY_N,
            uinput.KEY_O,
            uinput.KEY_P,
            uinput.KEY_V
        ])

        # Vars
        self.stream_process = 0
        self.player_process = 0
        self.is_cam_running = False
        #self.stream_cmd = '/usr/local/bin/mjpg_streamer -i "input_uvc.so -d /dev/video0 -y -f 30" -o "output_http.so -p 8090 -w /usr/local/www"'
        #self.player_cmd = '/usr/bin/omxplayer -r --live -b "http://localhost:8090/?action=stream" --layer=2'
        self.player_cmd = 'cd /home/pi/src/cam_overlay/; ./cam_overlay.bin'

    def increaseBrightness(self):
        current = bl.get_actual_brightness()
        target = current + 25
        if current < 255:
            if target > 255:
                target = 255
            bl.set_brightness(target, smooth=True, duration=1)

    def decreaseBrightness(self):
        current = bl.get_actual_brightness()
        target = current - 25
        if current > 11:
            if target < 11:
                target = 11
            bl.set_brightness(target, smooth=True, duration=1)

    def startCamera(self):
        if self.is_cam_running is False:
            try:
                print "Switching camera On"
                #self.stream_process = subprocess.Popen(self.stream_cmd, shell=True, preexec_fn=os.setsid)
                #print "Stream launched"
                #time.sleep(0.5)
                self.player_process = subprocess.Popen(self.player_cmd, shell=True, preexec_fn=os.setsid)
                print "Player launched"
                self.is_cam_running = True
            except:
                pass

    def volumeUp(self):
        try:
            subprocess.call('amixer -c1 sset Digital 1%+ > /dev/null')
        except:
            pass

    def volumeDown(self):
        try:
            subprocess.call('amixer -c1 sset Digital 1%- > /dev/null')
        except:
            pass

    def stopCamera(self):
        if self.is_cam_running:
            try:
                os.killpg(os.getpgid(self.player_process.pid), signal.SIGKILL)
                #time.sleep(0.5)
                #os.killpg(os.getpgid(self.stream_process.pid), signal.SIGKILL)
                self.is_cam_running = False
                print "Stopping camera"
            except:
                pass

    def handleCommand(self,cmd):
        if cmd == 'playpause':
            self.kbd.emit_click(uinput.KEY_B)
        elif cmd == 'next':
            self.kbd.emit_click(uinput.KEY_N)
        elif cmd == 'previous':
            self.kbd.emit_click(uinput.KEY_V)
        elif cmd == 'phoneUp':
            self.kbd.emit_click(uinput.KEY_P)
        elif cmd == 'phoneDown':
            self.kbd.emit_click(uinput.KEY_O)
        elif cmd == 'search':
            self.kbd.emit_click(uinput.KEY_M)
        elif cmd == 'home':
            self.kbd.emit_click(uinput.KEY_H)
        elif cmd == 'brightnessUp':
            self.increaseBrightness()
        elif cmd == 'brightnessDown':
            self.decreaseBrightness()
        elif cmd == 'volumeUp':
            self.volumeUp()
        elif cmd == 'volumeDown':
            self.volumeDown()
        elif cmd == 'screenOff':
            bl.set_power(False)
        elif cmd == 'screenOn':
            bl.set_power(True)
        elif cmd == 'toggleScreen':
            if bl.get_power():
                bl.set_power(False)
            else:
                bl.set_power(True)
        elif cmd == 'toggleCamera':
            print "Camera is " + ("running" if self.is_cam_running else "not running")
            if self.is_cam_running:
                print "Stop camera"
                self.stopCamera()
            else:
                print "Start camera"
                self.startCamera()

irctl = IrCtl()

# Launch socket server for communication with IR software (LIRC)
PORT = 8888
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
print 'Socket created'

# Binding socket
try:
    s.bind(('', PORT))
except socket.error as msg:
    print 'Bind failed. Error code: ' + str(msg[0]) + ' Message:' + msg[1]
    sys.exit()

print 'Socket bind complete'
s.listen(10)
print 'Socket now listening'

while True:
    try:
        conn, addr = s.accept()
        cmd = conn.recv(64).rstrip()
        print 'Received command: "' + cmd + '"'
        irctl.handleCommand(cmd)
    except KeyboardInterrupt:
        irctl.stopCamera()
        s.close()
        break;
    except:
        irctl.stopCamera()
        s.close()
