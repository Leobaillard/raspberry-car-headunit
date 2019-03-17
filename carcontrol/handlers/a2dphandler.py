from kivy.event import EventDispatcher
from kivy.properties import BooleanProperty, StringProperty, NumericProperty
from kivy.logger import Logger
from kivy.clock import Clock


#Inspired from: https://raw.githubusercontent.com/zandemax/pcms/master/dbushelpers/a2dp.py

class A2DPHandler(EventDispatcher):

    connected = BooleanProperty(False)
    status = StringProperty('paused')
    title = StringProperty()
    artist = StringProperty()
    duration = NumericProperty()
    current_pos = NumericProperty()

    def __init__(self, bluetooth, dummy=False, *args, **kwargs):
        super(A2DPHandler, self).__init__(*args, **kwargs)
        self.dummy = dummy
        Logger.info('A2DP: Loading a2dp-module')
        bluetooth.bind(interfaces=self.on_interfaces_changed)
        self.bluetooth = bluetooth
        self.player = None
        self.on_interfaces_changed(self, self.bluetooth.interfaces)
        Clock.schedule_interval(self.on_update_tick, 0.5)

    def on_interfaces_changed(self, instance, value):
        Logger.info('On interfaces change')
        if 'org.bluez.MediaPlayer1' in value:
            path = value['org.bluez.MediaPlayer1']
            try:
                self.player = self.bluetooth.bus.get('org.bluez', path)
                self.player.PropertiesChanged.connect(self.on_property_changed)
                self.get_properties()
                self.connected = True
            except KeyError:
                Logger.error('A2DP: Could not get player object')
        else:
            self.connected = False
        Logger.info('A2DP connection status: {}'.format(self.connected))

    def get_properties(self):
        message = self.player.GetAll('org.bluez.MediaPlayer1')
        try:
            track = message['Track']
            self.current_pos = message['Position']
            self.status = message['Status']
            self.duration = track['Duration']
            self.title = track['Title']
            self.artist = track['Artist']
        except KeyError:
            pass  # Couldn't get some properties

    def on_update_tick(self, dt):
        if self.connected:
            self.get_properties()

    def on_property_changed(self, property, message, c):
        try:
            if 'Track' in message:
                track = message['Track']
                labels = {'title': track['Title'], 'artist': track['Artist'],
                          'duration': track['Duration']}
                self.title = labels['title']
                self.artist = labels['artist']
                self.duration = labels['duration']
            elif 'Status' in message:
                self.status = message['Status']
                print(self.status)
            elif 'Position' in message:
                self.current_pos = message['Position']
            print property, message
        except KeyError:
            pass

    def set_gui(self, gui):
        self.gui = gui

    def pause(self):
        if self.connected:
            self.player.Pause()

    def play(self):
        if self.connected:
            self.player.Play()

    def next(self):
        if self.connected:
            self.player.Next()

    def previous(self):
        if self.connected:
            self.player.Previous()
