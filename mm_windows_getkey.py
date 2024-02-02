# code extracted from getchlib since I couldn't get it to work right
# for both linux and windows in the same project files

from msvcrt import kbhit, getwch


def get_key_nonblocking():
    if kbhit():
        return getwch()
    return ''


def get_key_blocking():
    return getwch()
