from kivy.app import App

from components.baseview import BaseView
from handlers import BrightnessHandler,VolumeHandler


class UserInterface(App):
    DUMMY = True

    def __init__(self, **kwargs):
        super(UserInterface, self).__init__(**kwargs)

        # Init handlers
        self.brightnessHandler = BrightnessHandler(self.DUMMY)
        self.volumeHandler = VolumeHandler(self.DUMMY)

    def build(self):
        return BaseView()
