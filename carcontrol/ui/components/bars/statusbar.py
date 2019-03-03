from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
import time
from kivy.logger import Logger
from kivy.utils import get_color_from_hex
from kivy.garden.iconfonts import icon

from ui.components.popups import VolumePopup, BrightnessPopup


class StatusBar(BoxLayout):
    volume_icons = {
        'mute': 'fa-volume-mute',
        'off': 'fa-volume-off',
        'low': 'fa-volume-down',
        'mid': 'fa-volume',
        'high': 'fa-volume-up'
    }

    signal_icons = {
        '0': 'fa-signal-slash',
        '1': 'fa-signal-1',
        '2': 'fa-signal-2',
        '3': 'fa-signal-3',
        '4': 'fa-signal-4',
        '5': 'fa-signal',
    }

    def __init__(self, **kwargs):
        super(StatusBar, self).__init__(**kwargs)
        Clock.schedule_interval(self.on_tick, 1)
        Clock.schedule_once(self.after_init, 0)
        self.app = App.get_running_app()
        Logger.info('Statusbar (' + str(self.parent) + '): Init')

        # Bind events
        self.app.volumeHandler.bind(on_volume_change=self.on_volume_change, on_mute_change=self.on_mute_change)
        self.app.hfpHandler.bind(attention=self.on_hfp_attention_change)
        self.app.hfpHandler.bind(carrier=self.on_carrier_change)
        self.app.hfpHandler.bind(network_strength=self.on_signal_change)
        self.app.hfpHandler.bind(connected=self.on_hfp_connected)
        self.app.a2dpHandler.bind(connected=self.on_connected_change)

        self.activePopup = None

    def after_init(self, dt):
        # Set initial status
        self.volume_update(self.app.volumeHandler.current)
        self.on_carrier_change('', '')
        self.on_hfp_connected('', '')
        self.on_signal_change('', '')

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
            # Bind to display timer
            self.activePopup.bind(on_display_timer_end=self.on_popup_display_timer)

        else:
            self.app.root.remove_widget(self.activePopup)
            self.activePopup.cancel_timer()

            if isinstance(self.activePopup, popup_class):
                self.activePopup = None
            else:
                self.activePopup = popup_class(**args)
                self.app.root.add_widget(self.activePopup)

                # Bind to display timer
                self.activePopup.bind(on_display_timer_end=self.on_popup_display_timer)

    def on_popup_display_timer(self, handler):
        self.toggle_popup(self.activePopup.__class__, '')

    def on_tick(self, dt):
        self.ids.time.text = time.strftime('%H:%M')

    def on_volume_change(self, handler, *args):
        self.volume_update(handler.current)

    def on_mute_change(self, status):
        if status:
            self.ids.volume_icon.text = icon(self.volume_icons['mute'])
        else:
            self.on_volume_change(self.app.volumeHandler.current)

    def volume_update(self, value):
        if 0 <= value < 20:
            self.ids.volume_icon.text = icon(self.volume_icons['off'])
        elif 20 <= value < 60:
            self.ids.volume_icon.text = icon(self.volume_icons['low'])
        elif 60 <= value < 80:
            self.ids.volume_icon.text = icon(self.volume_icons['mid'])
        elif 80 <= value < 100:
            self.ids.volume_icon.text = icon(self.volume_icons['high'])

    def on_connected_change(self, instance, value):
        Logger.info('A2DP: connected state changed: {}'.format(value))
        # if value:
        #     self.ids.bluetooth_icon.color = get_color_from_hex('ffffffff')
        # else:
        #     self.ids.bluetooth_icon.color = get_color_from_hex('444444ff')

    def on_hfp_attention_change(self, instance, value):
        Logger.info('HFP: attention changed: {}'.format(value))

    def on_carrier_change(self, instance, value):
        Logger.info('HFP: carrier changed: {}'.format(value))
        if self.app.hfpHandler.carrier is not None:
            self.ids.carrier.text = self.app.hfpHandler.carrier
        else:
            self.ids.carrier.text = ''

    def on_signal_change(self, instance, value):
        Logger.info('HFP: signal changed: {}'.format(value))
        if self.app.hfpHandler.network_strength == 0:
            self.ids.cell_icon.text = icon(self.signal_icons['0'])
        elif 0 < self.app.hfpHandler.network_strength < 20:
            self.ids.cell_icon.text = icon(self.signal_icons['1'])
        elif 20 <= self.app.hfpHandler.network_strength < 40:
            self.ids.cell_icon.text = icon(self.signal_icons['2'])
        elif 40 <= self.app.hfpHandler.network_strength < 60:
            self.ids.cell_icon.text = icon(self.signal_icons['3'])
        elif 60 <= self.app.hfpHandler.network_strength < 80:
            self.ids.cell_icon.text = icon(self.signal_icons['4'])
        elif self.app.hfpHandler.network_strength >= 80:
            self.ids.cell_icon.text = icon(self.signal_icons['5'])

    def on_hfp_connected(self, instance, value):
        Logger.info('HFP: connected state changed: {}'.format(value))
        if self.app.hfpHandler.connected:
            self.ids.bluetooth_icon.color = get_color_from_hex('ffffffff')
            self.ids.cell_icon.color = get_color_from_hex('ffffffff')
            self.ids.batt_icon.color = get_color_from_hex('ffffffff')
        else:
            self.ids.bluetooth_icon.color = get_color_from_hex('444444ff')
            self.ids.cell_icon.color = get_color_from_hex('444444ff')
            self.ids.batt_icon.color = get_color_from_hex('444444ff')
            self.ids.carrier.text = ''
