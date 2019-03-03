from kivy.app import App
from popupbar import PopupBar
from kivy.clock import Clock
from kivy.properties import NumericProperty, BooleanProperty
from kivy.logger import Logger


class VolumePopup(PopupBar):
    current = NumericProperty(0)
    min = NumericProperty(0)
    max = NumericProperty(100)
    isMuted = BooleanProperty(False)

    def __init__(self, **kwargs):
        super(VolumePopup, self).__init__(**kwargs)
        self.app = App.get_running_app()

        # Get values if they were passed
        self.current = kwargs.get('current', 0)
        self.min = kwargs.get('min', 0)
        self.max = kwargs.get('max', 0)
        self.isMuted = kwargs.get('isMuted', False)

        # Bind events
        # FIXME touch_down has a retention effect
        self.ids.volume_slider.bind(on_touch_up=self.on_volume_change, on_touch_move=self.on_volume_change)

    def on_volume_change(self, obj, touch):
        if obj.collide_point(*touch.pos):
            # Reset display timer
            self.reset_display_timer()

            # Change volume setting
            self.app.volumeHandler.set_volume(obj.value)
