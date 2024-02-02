# we use getchlib library since this has blocking and non-blocking
# while getch has only blocking


# the following code was extraced from the getchlib library
from getchlib_term import buffering, Buffering
from getchlib_ctrl import *
import os
import sys
import time
import fcntl


class NoBufReader:
    def __init__(self, file):
        self.fileno = file.fileno
        self.encoding = file.encoding
        self.fd = self.fileno()
        self.file = file

    def read(self, size):
        return self.file.read(size)


def get_key_nonblocking(tout_seconds=0.1):
    return _getkey_nonblocking(tout_seconds, True)


def get_key_blocking():
    return _getkey_blocking()


def _getkey_nonblocking(tout=0.1, catch=False):
    char = ''
    buffer = buf(NoBufReader(sys.stdin), catch)
    e = False
    _time = time.time()
    _end = _time + tout
    while time.time() <= _end:
        try:
            a = next(buffer)
            if a:
                if not e:
                    e = True
                char += a
            else:
                if e:
                    break
        except KeyboardInterrupt:
            if not catch:
                raise
            if not e:
                e = True
            char += '\x03'

    return char


# noinspection PyUnusedLocal
def _getkey_blocking(tout=0.01, catch=False, echo=False):
    char = ''
    buffer = buf(NoBufReader(sys.stdin), catch)
    entering = False
    for c in buffer:
        if not c:
            if entering:
                break
        else:
            if not entering:
                entering = True
            char += c
    return char


def _getkey(blocking=True, tout=0.1, catch=False, echo=False):
    if blocking:

        key = _getkey_blocking(tout, catch)
    else:

        key = _getkey_nonblocking(tout, catch)

    if key.isprintable() and echo:
        buffering.on()

        print(key, end='', flush=True)
    return key


# noinspection PyUnboundLocalVariable,PyUnusedLocal
def getkey(blocking=True, tout=0.1, catch=False, echo=False):
    entering: bool
    char: str
    try:
        return parse_key(_getkey(blocking, tout, catch, echo))
    except KeyboardInterrupt:
        if not catch:
            raise
        if not entering:
            entering = True
        char += '\x03'

    finally:
        buffering.on()


# noinspection PyUnusedLocal
def buf(file, catch=False):
    fcntl.fcntl(file, fcntl.F_SETFL, os.O_NONBLOCK)

    with Buffering(file):
        res = ''
        while True:
            try:
                a = file.read(1)
            except KeyboardInterrupt:
                if not catch:
                    raise
                a = '\x03'
            yield a
