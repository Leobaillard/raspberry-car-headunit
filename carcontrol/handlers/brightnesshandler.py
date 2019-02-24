from kivy.event import EventDispatcher
from kivy.logger import Logger
from kivy.properties import NumericProperty, BooleanProperty
import rpi_backlight as bl


class BrightnessHandler(EventDispatcher):
    current = NumericProperty()
    max = NumericProperty()
    status = BooleanProperty(True)
    MIN_BRIGHTNESS = 11

    def __init__(self, dummy=False, *args, **kwargs):
        Logger.name = 'BrightnessHandler'
        Logger.info('BrightnessHandler: Loading brightness-module')

        # Dummy mode?
        self.dummy = dummy

        # Set initial values
        self.current = bl.get_actual_brightness() if not self.dummy else 0
        self.max = bl.get_max_brightness() if not self.dummy else 100
        self.status = bl.get_power() if not self.dummy else True

        # Register events
        self.register_event_type('on_brightness_change')
        self.register_event_type('on_power_change')
        super(BrightnessHandler, self).__init__(*args, **kwargs)

    def set_brightness(self, value):
        if self.MIN_BRIGHTNESS <= value <= self.max:
            if not self.dummy:
                bl.set_brightness(int(value))
            self.dispatch('on_brightness_change', value)
            Logger.info('BrightnessHandler: setting brightness to {}'.format(value))
        else:
            raise ValueError("Brightness value must be between {} and {}".format(self.MIN_BRIGHTNESS, self.max))

    def set_power(self, status):
        if isinstance(status, bool):
            if not self.dummy:
                bl.set_power(status)
            self.dispatch('on_power_change', status)
            Logger.info('BrightnessHandler: setting power to {}'.format(status))

    def on_brightness_change(self, value, *args):
        self.current = value

    def on_power_change(self, power_state, *args):
        self.status = power_state
