__author__ = 'Dan.Simon'

import winsound
import time

def timeSTR(sec):
    m,s = divmod(sec,60)
    h,m = divmod(m,60)
    return "%d:%02d:%02d" % (int(h), int(m), int(s))

def beep():
    winsound.Beep(500,100)
    time.sleep(0.5)
    winsound.Beep(500,100)
    time.sleep(0.5)
    winsound.Beep(500,100)

if __name__ == '__main__':
    beep()