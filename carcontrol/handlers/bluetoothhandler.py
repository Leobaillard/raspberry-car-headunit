from kivy.event import EventDispatcher
from kivy.properties import DictProperty
from kivy.logger import Logger
from kivy.support import install_gobject_iteration

import pydbus


# Inspired from: https://raw.githubusercontent.com/zandemax/pcms/master/dbushelpers/bluetooth.py

class BluetoothHandler(EventDispatcher):
    interfaces = DictProperty()
    modems = DictProperty()

    def __init__(self, dummy=False):
        install_gobject_iteration()
        self.dummy = dummy
        bus = pydbus.SystemBus()
        self.bus = bus
        self.bluez = bus.get('org.bluez', '/')
        self.ofono = bus.get('org.ofono', '/')
        self.bluez.InterfacesAdded.connect(self.on_interfaces_added)
        self.bluez.InterfacesRemoved.connect(self.on_interfaces_removed)
        self.get_interfaces()
        self.get_modems()

    def get_interfaces(self):
        objects = self.bluez.GetManagedObjects()
        for object in objects:
            for interface in objects[object]:
                if 'org.bluez' in interface:
                    self.interfaces[interface] = object
        Logger.info('Found {} bluez interfaces'.format(len(self.interfaces)))

    def get_modems(self):
        modems = self.ofono.GetModems()
        for modem in modems:
            self.modems[modem[0]] = modem[1]
            modem_obj = self.bus.get('org.ofono', modem[0])
            modem_obj.PropertyChanged.connect(self.on_property_changed)
        Logger.info('Found {} bluez modems'.format(len(self.modems)))

    def on_property_changed(self, property, value):
        for modem in self.modems:
            modem_obj = self.bus.get('org.ofono', modem)
            self.modems[modem] = modem_obj.GetProperties()

    def get_device_serial(self):
        for modem in self.modems:
            if self.modems[modem]['Online'] is True:
                modem = self.bus.get('org.ofono', modem)
                properties = modem.GetProperties()
                return properties['Serial']

    def on_interfaces_added(self, object, properties):
        for i in properties:
            if 'org.bluez' in i:
                interface = i
        self.interfaces[interface] = object

    def on_interfaces_removed(self, object, properties):
        for i in properties:
            if 'org.bluez' in i:
                interface = i
        self.interfaces.pop(interface, None)
