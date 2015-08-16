
from pyfirmata import Arduino, util

import time
import argparse
import yaml

config = None
with open('config.yml') as f:
    config = yaml.load(f)


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

        return ret
    
    def __init__(self):
        self.board = Arduino(config['port'])

        self.pin_led = self.board.get_pin('d:%d:p' % (config['light']['pin'],))
        self.pin_photo = self.board.get_pin('a:%d:i' % (config['photoresistor']['pin'],))
        self.pin_13 = self.board.get_pin('d:13:o')

        self._iter = util.Iterator(self.board)
        self._iter.start()

        self.pin_photo.enable_reporting()

    def close(self):
        self.board.exit()

        # Kill the _iter thread
        self._iter.board = None

    def blink13(self):
        while True:
            self.pin_13.write(1)
            time.sleep(1)
            self.pin_13.write(0)
            time.sleep(1)


commands = {}


def command(cls):
    if cls.name is None:
        raise NotImplementedError("Class did not specify command name")

    if cls.help is None:
        raise NotImplementedError("Class did not specify help message")

    commands[cls.name] = cls


class CommandBase(object):
    name = None
    help = None

    def __init__(self, brd):
        self.board = brd

    def setup_arg_parser(self, parser):
        raise NotImplementedError()

    def execute(self, args):
        raise NotImplementedError()


@command
class Light(CommandBase):
    name = 'light'
    help = 'Set light brightness level'

    def setup_arg_parser(self, parser):
        parser.add_argument('level', type=int, choices=range(0, 101), metavar='{0..100}',
                            help='Light brightness from 0 to 100')

    def execute(self, args):
        self.board.light_level = args.level


@command
class Blink13(CommandBase):
    name = 'blink13'
    help = 'Blink the LED on pin 13'

    def setup_arg_parser(self, parser):
        pass

    def execute(self, args):
        self.board.blink13()


@command
class Print(CommandBase):
    name = 'print'
    help = 'Print hooks'

    def setup_arg_parser(self, parser):
        parser.add_argument('event', choices=['start', 'stop'], help='Print event to respond to')

    def execute(self, args):
        if args.event == 'start':
            photo = self.board.photoresistor_level
            if photo <= config['photoresistor']['level']:
                self.board.light_level = config['light']['level']
        elif args.event == 'stop':
            self.board.light_level = 0


@command
class Photoresistor(CommandBase):
    name = 'photoresistor'
    help = 'Report the current photoresistor value'

    def setup_arg_parser(self, parser):
        pass

    def execute(self, args):
        print self.board.photoresistor_level


def main():
    board = Board()

    root_parser = argparse.ArgumentParser(description='OctoPrint Auxiliary functionality')

    subparsers = root_parser.add_subparsers()

    for key in commands:
        cls = commands[key]
        parser = subparsers.add_parser(cls.name, help=cls.help)
        cls = cls(board)
        cls.setup_arg_parser(parser)
        parser.set_defaults(name=key)
        commands[key] = cls

    try:
        arguments = root_parser.parse_args()
        commands[arguments.name].execute(arguments)
    finally:
        board.close()

if __name__ == '__main__':
    main()