from kivy.app import App
from popupbar import PopupBar
from kivy.properties import NumericProperty, BooleanProperty


class BrightnessPopup(PopupBar):
    current = NumericProperty(0)
    min = NumericProperty(0)
    max = NumericProperty(255)
    status = BooleanProperty(True)

    def __init__(self, **kwargs):
        super(BrightnessPopup, self).__init__(**kwargs)
        self.app = App.get_running_app()

        # Get values if they were passed
        self.current = kwargs.get('current', 0)
        self.min = kwargs.get('min', 0)
        self.max = kwargs.get('max', 255)
        self.status = kwargs.get('status', True)

        # Bind events
        # FIXME touch_down has a retention effect
        self.ids.brightness_slider.bind(on_touch_up=self.on_brightness_change,
                                        on_touch_move=self.on_brightness_change)

    def on_brightness_change(self, obj, touch):
        if obj.collide_point(*touch.pos):
            self.app.brightnessHandler.set_brightness(obj.value)
