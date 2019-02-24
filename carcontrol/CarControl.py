import os

os.environ['KIVY_GL_BACKEND'] = 'gl'
import kivy

from kivy.config import Config
from kivy.garden.iconfonts import iconfonts

from ui.ui import UserInterface

kivy.require('1.11.0')

FONT_DIR = os.path.join('assets', 'fonts')


class CarControlApp:
    def __init__(self):
        # Set window size
        Config.set('graphics', 'width', '800')
        Config.set('graphics', 'height', '480')

        # Load fonts
        self.generateFontFiles()
        iconfonts.register('font-awesome', os.path.join(FONT_DIR, 'font-awesome.ttf'),
                           os.path.join(FONT_DIR, 'font-awesome.fontd'))

    def generateFontFiles(self):
        if not os.path.exists(os.path.join(FONT_DIR, 'font-awesome.fontd')) and \
                os.path.exists(os.path.join(FONT_DIR, 'font-awesome.ttf')) and \
                os.path.exists(os.path.join(FONT_DIR, 'font-awesome.css')):
            # Font definition has to be created
            iconfonts.create_fontdict_file(os.path.join(FONT_DIR, 'font-awesome.css'),
                                           os.path.join(FONT_DIR, 'font-awesome.fontd'))

    @staticmethod
    def run():
        UserInterface().run()


if __name__ == '__main__':
    CarControlApp().run()
