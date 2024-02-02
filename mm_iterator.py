import time

from rich.console import Console
from mm_misc import is_windows

is_windows: bool

if is_windows():
    is_windows = True
    from mm_windows_getkey import get_key_blocking, get_key_nonblocking
else:
    is_windows = False
    from mm_linux_getkey import get_key_blocking, get_key_nonblocking


def is_validy_move(test_str: str) -> bool:
    v_files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    v_ranks = ['1', '2', '3', '4', '5', '6', '7', '8']
    if len(test_str) != 4:
        return False
    return test_str[0] in v_files and test_str[1] in v_ranks and test_str[2] in v_files and test_str[3] in v_ranks


class MinIterator():
    def get_valid_command(self, some_console: Console) -> str:
        valid_commands = ['i', 'q']
        caught_key = 'x'
        while caught_key not in valid_commands:
            some_console.print('\n MinMater++➤ ', style='cyan on default', end='')
            caught_key = get_key_blocking().lower()
            some_console.print(caught_key, end='')
            if caught_key not in valid_commands:
                some_console.print('     valid commands are <i> for iterate and <q> to quit', style='red on default',
                                   end='')
                time.sleep(1.0)
        return caught_key

    def get_valid_iterate_subcommands(self, some_console: Console) -> str:
        cl_valid = False
        some_console.print()
        cl = ''
        while not cl_valid:
            some_console.print('     iterate - user color (must be playing from bottom of board) - specify "w" for white, "b" for black: ', end='')
            cl = input().lower()
            if cl == 'w' or cl == 'b':
                cl_valid = True
            else:
                some_console.print('         try again', style='red on default', end='\n')

        mm_valid = False
        mm = ''
        while not mm_valid:
            some_console.print('     iterate - move to make (e.g., e2e4): ', end='')
            mm = input().lower()
            if is_validy_move(mm):
                mm_valid = True
            else:
                some_console.print('         try again', style='red on default', end='\n')

        rm_valid = False
        rm = ''
        while not rm_valid:
            some_console.print('     iterate - desired response mode - specify "i" for include (default), "e" for exclude: ', end='')
            rm = input().lower()
            if rm == 'i' or rm == 'e' or rm == '':
                rm_valid = True
                if rm == '':
                    rm = 'i'
            else:
                some_console.print('         try again', style='red on default', end='\n')

        moves_valid = False
        incl_excl = 'include' if rm == 'i' else 'exclude'
        moves = ''
        while not moves_valid:
            some_console.print(f'     iterate - moves to {incl_excl} (algebraic format, proper case for pieces, separated by spaces): ', end='')
            moves = input()
            moves_list = moves.split(' ')
            if len(moves_list) > 0:
                moves_valid = True
            # for move in moves_list:
            #     if not is_validy_move(move):
            #         moves_valid = False
            #         break
            if not moves_valid:
                some_console.print('         try again', style='red on default', end='\n')

        limit_valid = False
        limit = ''
        while not limit_valid:
            some_console.print('     iterate - number of attempts to limit to (default is unlimited): ', end='')
            limit = input().lower().strip()
            if limit == '':
                limit = '0'
                limit_valid = True
            else:
                try:
                    limit_num = int(limit)
                    if limit_num > 0:
                        limit_valid = True
                except:
                    some_console.print('         try again', style='red on default', end='\n')
                if not limit_valid:
                    some_console.print('         try again', style='red on default', end='\n')

        move_num_to_make_valid = False
        move_num_to_make = ''
        while not move_num_to_make_valid:
            some_console.print('     iterate - move number to make: ', end='')
            move_num_to_make = input().lower().strip()
            try:
                move_num_int = int(move_num_to_make)
                move_num_to_make_valid = True
                move_num_to_make = str(move_num_int)
            except:
                move_num_to_make_valid = False
                some_console.print('         try again', style='red on default', end='\n')
                continue
            if move_num_to_make == '':
                some_console.print('         try again', style='red on default', end='\n')

        return cl + ' ' + mm + ' ' + rm + ' ' + limit + ' ' + move_num_to_make + ' ' + moves
