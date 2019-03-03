from kivy.app import App

from components.baseview import BaseView
from handlers import BrightnessHandler,VolumeHandler, BluetoothHandler, HFPHandler, A2DPHandler


class UserInterface(App):
    DUMMY = True

    def __init__(self, **kwargs):
        super(UserInterface, self).__init__(**kwargs)

        # Init handlers
        self.brightnessHandler = BrightnessHandler(self.DUMMY)
        self.volumeHandler = VolumeHandler(self.DUMMY)
        self.bluetoothHandler = BluetoothHandler(self.DUMMY)
        self.hfpHandler = HFPHandler(self.bluetoothHandler, self.DUMMY)
        self.a2dpHandler = A2DPHandler(self.bluetoothHandler, self.DUMMY)

    def build(self):
        return BaseView()
