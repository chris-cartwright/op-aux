
from pyfirmata import Arduino, util

import time
import config
import argparse


class Board(object):
    _light_level = 0
    
    @property
    def light_level(self):
        return self._light_level
    
    @light_level.setter
    def light_level(self, level):
        level = int(level)
    
        if level < 0:
            level = 0
        elif level > 100:
            level = 100
        
        self._light_level = level
        self.pin_led.write(level / 100.0)
        
    @property
    def photoresistor_level(self):
        ret = None
        count = 0
        while ret is None and count < 10:
            count += 1
            time.sleep(0.01)
            ret = self.pin_photo.read()

        print count
        return ret
    
    def __init__(self):
        self.board = Arduino(config.port)

        self.pin_led = self.board.get_pin('d:%d:p' % (config.light['pin'],))
        self.pin_photo = self.board.get_pin('a:%d:i' % (config.photoresistor['pin'],))
        self.pin_13 = self.board.get_pin('d:13:o')

        self._iter = util.Iterator(self.board)
        self._iter.start()

        self.pin_photo.enable_reporting()

    def __del__(self):
        self.board.exit()

        # Kill the _iter thread
        self._iter.board = None
            
    def blink13(self):
        while True:
            self.pin_13.write(1)
            time.sleep(1)
            self.pin_13.write(0)
            time.sleep(1)


def cmd_light(a):
    board = Board()
    board.light_level = a.level


def cmd_blink13(a):
    board = Board()
    board.blink13()


def cmd_print(a):
    board = Board()
    
    if a.event == 'start':
        photo = board.photoresistor_level
        if photo <= config.photoresistor['level']:
            board.light_level = config.light['level']
    elif a.event == 'stop':
        board.light_level = 0


def cmd_photoresistor(a):
    board = Board()
    print board.photoresistor_level

root_parser = argparse.ArgumentParser(description='OctoPrint Auxiliary functionality')

subparsers = root_parser.add_subparsers()

light_parser = subparsers.add_parser('light', help='Set light brightness level')
light_parser.add_argument('level', type=int, choices=range(0, 101), metavar='{0..100}',
                          help='Light brightness from 0 to 100')
light_parser.set_defaults(func=cmd_light)

blink13_parser = subparsers.add_parser('blink13', help='Blink the LED on pin 13')
blink13_parser.set_defaults(func=cmd_blink13)

photoresistor_parser = subparsers.add_parser('photoresistor', help='Report the current photoresistor value')
photoresistor_parser.set_defaults(func=cmd_photoresistor)

print_parser = subparsers.add_parser('print', help='Print hooks')
print_parser.add_argument('event', choices=['start', 'stop'], help='Print event to respond to')
print_parser.set_defaults(func=cmd_print)

args = root_parser.parse_args()
args.func(args)
