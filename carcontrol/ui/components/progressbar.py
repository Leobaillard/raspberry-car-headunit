from kivy.uix.relativelayout import RelativeLayout
from kivy.properties import NumericProperty

# Inspired from: https://raw.githubusercontent.com/zandemax/pcms/master/ui/components/progressbar.py

kv = '''

<ProgressBarColor>
    canvas.before:
        Color:
            rgba: 1, 1, 1, 1
        Rectangle:
            pos: self.pos
            size: self.size
        Color:
            rgba: .5 , 1, 1, 1
        Rectangle:
            pos: self.pos
            height: self.height
            width: root.bar_width
'''


class ProgressBarColor(RelativeLayout):

    value = NumericProperty()
    bar_width = NumericProperty()

    def __init__(self, **kwargs):
        super(ProgressBarColor, self).__init__(**kwargs)
        self.value = 0
        self.bind(value=self.on_value_change)

    def on_value_change(self, instance, value):
        if value > 1:
            value = 1
        elif value < 0:
            value = 0
        self.bar_width = self.width / value
