import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'
from pygame import mixer
from time import sleep


def play_sound(filename: str, duration: float) -> None:
    mixer.music.load(filename)
    mixer.music.play()
    sleep(duration)


def play_winning_sound() -> None:
    play_sound('./sounds/wow.mp3', 3.0)  # file is actually 6 seconds long, but becomes virtually silent after 3


def play_losing_sound() -> None:
    play_sound('./sounds/horn.mp3', 4.0)
