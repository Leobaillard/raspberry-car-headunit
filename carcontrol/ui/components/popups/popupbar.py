from kivy.uix.floatlayout import FloatLayout
from kivy.event import EventDispatcher
from kivy.clock import Clock
from kivy.logger import Logger


class PopupBar(FloatLayout, EventDispatcher):
    def __init__(self, **kwargs):
        super(PopupBar, self).__init__(**kwargs)
        self.displayTimer = None

        # Register event
        self.register_event_type('on_display_timer_end')

        # Set display timer
        self.displayTimer = Clock.schedule_once(self.on_display_timer, 5)
        self.displayTimer()

    def reset_display_timer(self):
        # Reset display timer
        self.displayTimer.cancel()
        self.displayTimer = Clock.schedule_once(self.on_display_timer, 5)

    def on_display_timer(self, dt):
        # When timer is up, hide the popup
        self.dispatch('on_display_timer_end')

    def on_display_timer_end(self, *args):
        Logger.info('Event: on_display_timer_end')

    def cancel_timer(self):
        self.displayTimer.cancel()
