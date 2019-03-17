from kivy.app import App
from kivy.support import install_gobject_iteration
from kivy.logger import Logger
from kivy.utils import get_color_from_hex

from components.baseview import BaseView
from handlers import BrightnessHandler, VolumeHandler, BluetoothHandler, HFPHandler, A2DPHandler


class UserInterface(App):
    DUMMY = True

    def __init__(self, **kwargs):
        super(UserInterface, self).__init__(**kwargs)

        # Init handlers
        self.view = None
        self.brightnessHandler = BrightnessHandler(self.DUMMY)
        self.volumeHandler = VolumeHandler(self.DUMMY)
        self.bluetoothHandler = BluetoothHandler(self.DUMMY)
        self.hfpHandler = HFPHandler(self.bluetoothHandler, self.DUMMY)
        self.a2dpHandler = A2DPHandler(self.bluetoothHandler, self.DUMMY)

    def build(self):
        install_gobject_iteration()

        self.view = BaseView()

        # Bind events
        self.view.ids.control_bar.bind(on_screen_switch=self.on_screen_switch)

        return self.view

    def on_screen_switch(self, instance, screen, *args):
        if screen == 'home':
            self.view.ids.screenmanager.current = 'home_screen'
        elif screen == 'media':
            self.view.ids.screenmanager.current = 'media_screen'
        elif screen == 'phone':
            self.view.ids.screenmanager.current = 'phone_screen'

        for screen in self.view.ids.screenmanager.screens:
            if screen.name == self.view.ids.screenmanager.current:
                self.view.ids.control_bar.ids[screen.name + '_btn'].color = get_color_from_hex('FFFFFFFF')
            else:
                self.view.ids.control_bar.ids[screen.name + '_btn'].color = get_color_from_hex('444444FF')