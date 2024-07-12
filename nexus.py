import pyautogui as pt
from time import sleep

import os.path

class Clicker:
    def __init__(self, target, speed):
        self.target = target
        self.speed = speed
        pt.FAILSAFE = True

    def nav(self):
        try:
            print("searching")
            pos = pt.locateOnScreen(self.target, grayscale=True, confidence=.8)
            pt.moveTo(pos[0] -55, pos[1] + 15, duration=self.speed)
            pt.click()
            sleep(2)
        except:
            print("img not found")
            return 0

            
if __name__ == '__main__':
    clicker = Clicker('nexus.png', speed=.001)
    end = 0
    pt.moveTo(1000,900)
    sleep(2)
    t = pt.locateCenterOnScreen("F:/nexus.png")
    print(t)
    while True:
        if clicker.nav() == 0:
            end += 1
        sleep(5)
