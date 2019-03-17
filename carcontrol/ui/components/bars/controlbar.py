from kivy.app import App
from kivy.uix.widget import Widget
from kivy.event import EventDispatcher
from kivy.logger import Logger


class ControlBar(Widget, EventDispatcher):

    def __init__(self, **kwargs):
        super(ControlBar, self).__init__()
        self.app = App.get_running_app()

        # Register events
        self.register_event_type('on_screen_switch')

    def switch_screen(self, instance):
        screen = 'home'
        if instance == self.ids.home_screen_btn:
            screen = 'home'
        elif instance == self.ids.media_screen_btn:
            screen = 'media'
        elif instance == self.ids.phone_screen_btn:
            screen = 'phone'

        self.dispatch('on_screen_switch', screen)

    def on_screen_switch(self, screen, *args):
        pass
