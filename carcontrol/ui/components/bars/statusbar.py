from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
import time
from kivy.logger import Logger
from kivy.garden.iconfonts import icon

from ui.components.popups import VolumePopup, BrightnessPopup


class StatusBar(BoxLayout):
    volume_icons = {
        'mute': 'fa-volume-mute',
        'low': 'fa-volume-down',
        'mid': 'fa-volume',
        'high': 'fa-volume-up'
    }

    def __init__(self, **kwargs):
        super(StatusBar, self).__init__(**kwargs)
        Clock.schedule_interval(self.on_tick, 1)
        self.app = App.get_running_app()
        Logger.info('Statusbar (' + str(self.parent) + '): Init')

        # Bind events
        self.app.volumeHandler.bind(on_volume_change=self.on_volume_change, on_mute_change=self.on_mute_change)

        self.activePopup = None

    def volume_clicked(self):
        self.toggle_popup(VolumePopup,
                          {'current': self.app.volumeHandler.current, 'isMuted': self.app.volumeHandler.isMuted,
                           'min': self.app.volumeHandler.MIN_VOL, 'max': self.app.volumeHandler.MAX_VOL})

    def brightness_clicked(self):
        self.toggle_popup(BrightnessPopup,
                          {'current': self.app.brightnessHandler.current, 'status': self.app.brightnessHandler.status,
                           'min': self.app.brightnessHandler.MIN_BRIGHTNESS, 'max': self.app.brightnessHandler.max})

    def toggle_popup(self, popup_class, args):
        if self.activePopup is None:
            self.activePopup = popup_class(**args)
            self.app.root.add_widget(self.activePopup)
        else:
            self.app.root.remove_widget(self.activePopup)

            if isinstance(self.activePopup, popup_class):
                self.activePopup = None
            else:
                self.activePopup = popup_class(**args)
                self.app.root.add_widget(self.activePopup)

    def on_tick(self, dt):
        self.ids.time.text = time.strftime('%H:%M')

    def on_volume_change(self, handler, *args):
        value = handler.current
        if 0 <= value < 60:
            self.ids.volume_icon.text = icon(self.volume_icons['low'])
        elif 60 <= value < 80:
            self.ids.volume_icon.text = icon(self.volume_icons['mid'])
        elif 80 <= value < 100:
            self.ids.volume_icon.text = icon(self.volume_icons['high'])

    def on_mute_change(self, status):
        if status:
            self.ids.volume_icon.text = icon(self.volume_icons['mute'])
        else:
            self.on_volume_change(self.app.volumeHandler.current)
