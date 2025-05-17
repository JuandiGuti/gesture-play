import random

GESTOS = ["play_pause", "next", "prev", "vol_up", "vol_down"]

def detectar_gesto():
    return random.choice(GESTOS)
