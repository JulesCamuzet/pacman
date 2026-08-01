from pydantic import BaseModel
from enum import Enum
import pygame


class SoundsEnum(Enum):
    """
    List the differents sound in the game.
    """

    EAT_PACGUM = 0
    GHOST_EATER = 1
    WIN = 2
    EAT_GHOST = 3


mapping_sound_enum_and_filepath: dict[SoundsEnum, str] = {
    SoundsEnum.EAT_PACGUM: "assets/audio/i.mp3",
    SoundsEnum.GHOST_EATER: "assets/audio/bark-bark-marex.mp3",
    SoundsEnum.WIN: "assets/audio/mais-lets-go-marex.mp3",
    SoundsEnum.EAT_GHOST: "assets/audio/i.mp3",
}


mapping_sound_enum_and_channel: dict[SoundsEnum, int] = {
    SoundsEnum.EAT_PACGUM: 0,
    SoundsEnum.GHOST_EATER: 1,
    SoundsEnum.WIN: 2,
    SoundsEnum.EAT_GHOST: 3,
}


class SoundManager(BaseModel):
    """
    Manage the game sounds.
    """

    def init(self) -> None:
        """
        Init the pygame mixer.
        """

        pygame.mixer.set_num_channels(4)

    def play_sound(self, sound: SoundsEnum) -> None:
        """
        Play a sound.
        """

        filename = mapping_sound_enum_and_filepath[sound]
        channel = mapping_sound_enum_and_channel[sound]

        if sound == SoundsEnum.GHOST_EATER:
            loops = -1
        else:
            loops = 0

        pygame.mixer.Channel(channel).play(
            pygame.mixer.Sound(filename),
            loops=loops
        )

    def stop_sound(self, sound: SoundsEnum) -> None:
        """
        Stop a sound.
        """

        channel = mapping_sound_enum_and_channel[sound]
        pygame.mixer.Channel(channel).stop()
