from kivy.app import App
from kivy.uix.screenmanager import Screen
from math import floor
from kivy.clock import Clock
from kivy.garden.iconfonts import icon


import locale

locale.setlocale(locale.LC_TIME, '')
import time
from kivy.logger import Logger


class MediaScreen(Screen):
    def __init__(self, **kwargs):
        super(MediaScreen, self).__init__(**kwargs)
        self.app = App.get_running_app()

        # Binding events
        self.app.a2dpHandler.bind(title=self.on_title_change)
        self.app.a2dpHandler.bind(artist=self.on_artist_change)
        self.app.a2dpHandler.bind(duration=self.on_duration_change)
        self.app.a2dpHandler.bind(current_pos=self.on_duration_change)
        self.app.a2dpHandler.bind(connected=self.on_connected_change)
        self.app.a2dpHandler.bind(status=self.on_status_change)

        # Binding actions
        # self.ids.play_btn.bind(on_release=self.on_play)
        # self.ids.previous_btn.bind(on_release=self.on_previous)
        # self.ids.next_btn.bind(on_release=self.on_next)

        # Set initial values after init is done
        Clock.schedule_once(self.set_initial_status, 0)

    def set_initial_status(self, dt):
        self.on_title_change(None, None)
        self.on_artist_change(None, None)
        self.on_duration_change(None, None)
        self.on_connected_change(None, None)
        self.on_status_change(None, None)

    def on_title_change(self, instance, value):
        self.ids.title.text = self.app.a2dpHandler.title

    def on_artist_change(self, instance, value):
        self.ids.artist.text = self.app.a2dpHandler.artist

    def on_duration_change(self, instance, value):
        if self.app.a2dpHandler.status == 'playing':
            self.ids.elapsed.text = str(int(floor(self.app.a2dpHandler.current_pos / (1000 * 60)) % 60)) + ':' + str(
                int(floor(self.app.a2dpHandler.current_pos / 1000) % 60)).zfill(2)
            try:
                self.ids.progress.value = (self.app.a2dpHandler.current_pos / self.app.a2dpHandler.duration) * 100
            except ZeroDivisionError:
                print 'zerodiv'
                pass
            return True
        else:
            return True

    def on_connected_change(self, instance, value):
        pass

    def on_status_change(self, instance, value):
        if self.app.a2dpHandler.status == 'playing':
            self.ids.play_btn.text = icon('fa-pause')
        else:
            self.ids.play_btn.text = icon('fa-play')

    def on_play(self):
        if self.app.a2dpHandler.status == 'paused':
            self.app.a2dpHandler.play()
        else:
            self.app.a2dpHandler.pause()

    def on_previous(self):
        self.app.a2dpHandler.previous()

    def on_next(self):
        self.app.a2dpHandler.next()