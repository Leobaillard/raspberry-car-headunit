import sys
from kivy.event import EventDispatcher
from kivy.logger import Logger
from kivy.properties import NumericProperty, BooleanProperty
import alsaaudio


class VolumeHandler(EventDispatcher):
    current = NumericProperty()
    isMuted = BooleanProperty(False)
    cardIndex = 0
    mixer = None
    MIN_VOL = 0
    MAX_VOL = 100
    CARD_NAME = 'sndrpihifiberry'
    MIXER_NAME = 'Digital'

    def __init__(self, dummy=False, *args, **kwargs):
        Logger.info('VolumeHandler: Loading volume-module')
        Logger.name = 'VolumeHandler'

        # Dummy mode?
        self.dummy = dummy
        if self.dummy:
            self.MIXER_NAME = 'Master'

        # Find sound card
        try:
            self.cardIndex = alsaaudio.cards().index(self.CARD_NAME)
        except ValueError:
            Logger.warning('Sound card "{}" has not been found! Selected default card.'.format(self.CARD_NAME))

        # Find mixer
        try:
            self.mixer = alsaaudio.Mixer(self.MIXER_NAME, cardindex=self.cardIndex)
        except alsaaudio.ALSAAudioError:
            Logger.critical('Could not find mixer "{}" on card "{}"! Aborting.'.format(self.MIXER_NAME, self.cardIndex))
            sys.exit(1)

        # Set initial values
        self.isMuted = bool(self.mixer.getmute()[0])  # We only get one channel but the two should be in sync anyway
        self.current = int(self.mixer.getvolume()[0])

        # Register events
        self.register_event_type('on_volume_change')
        self.register_event_type('on_mute_change')

        super(VolumeHandler, self).__init__(*args, **kwargs)

    def set_volume(self, value):
        if self.MIN_VOL <= value <= self.MAX_VOL:
            self.mixer.setvolume(int(value))
            self.dispatch('on_volume_change', value)
            Logger.info('VolumeHandler: setting volume to {}'.format(value))
        else:
            raise ValueError("Volume value must be between {} and {}".format(self.MIN_VOL, self.MAX_VOL))

    def set_mute(self, status):
        if isinstance(status, bool):
            self.mixer.setmute(status)
            self.dispatch('on_mute_change', status)
            Logger.info('VolumeHandler: setting mute status to {}'.format(status))

    def on_volume_change(self, value, *args):
        self.current = value

    def on_mute_change(self, status, *args):
        self.isMuted = status
