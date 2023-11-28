import os
import time

while True:
    os.system("git pull")
    time.sleep(2)
    os.system("python3 bot.py")
    time.sleep(5)
