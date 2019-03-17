from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
import locale

from kivy.logger import Logger


class PhoneScreen(Screen):
    def __init__(self, **kwargs):
        super(PhoneScreen, self).__init__(**kwargs)
        self.app = App.get_running_app()