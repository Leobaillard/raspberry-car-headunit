from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
import locale

locale.setlocale(locale.LC_TIME, '')
import time
from kivy.logger import Logger


class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super(HomeScreen, self).__init__(**kwargs)
        Clock.schedule_interval(self.on_tick, 1)
        self.app = App.get_running_app()
        Logger.info('Statusbar (' + str(self.parent) + '): Init')

    def on_tick(self, dt):
        self.ids.time_lbl.text = time.strftime('%H:%M')
        self.ids.date_lbl.text = time.strftime('%a, %d %B %Y')
