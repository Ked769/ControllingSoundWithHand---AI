import os
from pynput import *

def on_press(key):
    if key == keyboard.Key.delete:
        os.system("taskkill /f /im main.exe")
        exit()
        return False
def on_release(key):
    return 0;
with keyboard.Listener(on_press = on_press, on_release = on_release) as listener:
    listener.join()