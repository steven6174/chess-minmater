#!/home/steven/PycharmProjects/MinMater++/venv/bin/python3.10
import time

# Program: MainMater++
# Purpose: Play chess.com games by iterating moves until desired outcome is achieved

# global variable, moved up here due to order
is_windows: bool

# imports: start ##############
# import (a): project files
from mm_chess_engine import *
from mm_chess_game import *
from mm_chrome import *
from mm_enums import Player_Color
from mm_inputs import *
from mm_misc import clear_console, is_windows

if is_windows():
    is_windows = True
    from mm_windows_getkey import get_key_blocking, get_key_nonblocking
else:
    is_windows = False
    from mm_linux_getkey import get_key_blocking, get_key_nonblocking
import mm_logging
from mm_sounds import *
from mm_iterator import MinIterator

# import (b): Rich
from rich.console import Console
from rich.traceback import install

install()  # suppress=[click]

# import (c): other
from chess import Board, Move
from logging import Logger
import os

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'
import pygame
from selenium import webdriver
from selenium.common.exceptions import ElementClickInterceptedException

# imports: end ################


# global variables: start #####
chrome_driver: webdriver
chess_engine: Engine
this_console: Console
mm_logger: Logger


# global variables: end #######


def initialize() -> None:
    global this_console, mm_logger
    this_console = Console(color_system='truecolor')

    running_directory = os.path.dirname(os.path.realpath(__file__))
    os.chdir(running_directory)
    clear_console()

    mm_logger = mm_logging.get_app_logger()

    pygame.init()
    pygame.mixer.init()


def clean_up(driver: webdriver) -> None:
    this_console.print('---> Quitting pygame')
    pygame.mixer.quit()
    pygame.quit()
    this_console.print('---> Closing Chrome')
    close_chrome_driver(driver, is_windows)
    this_console.print('Complete\n')


def abort_program(return_val: int = 0, error_text: str = '') -> None:
    if error_text != '':
        this_console.print('\n\n' + error_text, style='bold red on black')
    this_console.print('\n\nClosing initiated')
    try:
        clean_up(chrome_driver)
    except NameError:  # in case program aborted before chrome_driver is defined
        pass
    except:
        pass
    time.sleep(1.0)  # to look a bit more professional
    exit(return_val)


def pretty_print_moves(dict_moves: {}) -> None:
    sorted_move_list = sorted(dict_moves.items(), key=lambda x: x[1], reverse=True)
    move_list_wo_space = str(sorted_move_list).replace(' ', '')
    move_list_wo_space_ticks = move_list_wo_space.replace("'", '')
    move_list_wo_space_ticks_etc = move_list_wo_space_ticks.replace('),', '-').replace('(', '')
    this_console.print(move_list_wo_space_ticks, sep='')


def print_program_intro():
    this_console.print('MinMater++ - Iterating Edition', style='bold #ffffff on #ff0000', justify='center')
    this_console.print('Copyright © [white]2022[/white]', style='#ffffff on #cf0030', justify='center')
    this_console.print('Steven Kendrick', style='italic #ffffff on #cf0030', justify='center')


def main() -> None:
    global this_console, chrome_driver, chess_engine
    initialize()
    time.sleep(0.5)
    print_program_intro()

    chrome_driver = get_chrome_driver(is_win=is_windows)

    # this_console.print('\nPress [bold cyan]<ENTER>[/bold cyan] once you are ready to start iterating, [bold cyan]Q[/bold cyan] to quit',
    #                    style='#65a4cf')
    # if get_key_blocking().lower() == 'q':
    #     this_console.print('\n\nOK', style='cyan')
    #     abort_program(0)
    # time.sleep(1.0)
    # user_color = determine_user_color(chrome_driver)
    # white_on_top = is_white_on_top(chrome_driver)
    min_iterator = MinIterator()

    command_key = 'x'
    while command_key != 'q':
        command_key = min_iterator.get_valid_command(this_console)
        # this_console.print(f'command_key is {command_key}', end='')
        if command_key == 'i':
            # user_color = determine_user_color(chrome_driver)
            # user_color = Player_Color.WHITE
            # user_color = Player_Color.BLACK
            # white_on_top = is_white_on_top(chrome_driver)
            # white_on_top = False
            # white_on_top = True
            iterate_params = min_iterator.get_valid_iterate_subcommands(this_console)
            comps = iterate_params.split(' ')  # .lower().split(' ')
            user_cl = comps[0]
            user_color = Player_Color.WHITE if user_cl == 'w' else Player_Color.BLACK
            computer_color = Player_Color.BLACK if user_color == Player_Color.WHITE else Player_Color.WHITE
            white_on_top = user_color == Player_Color.BLACK
            move_to_make = comps[1]
            incl_excl = comps[2].lower()
            limit_trials = int(comps[3])
            move_num_to_make = int(comps[4])  # + (1 if user_color == Player_Color.BLACK else 0)
            num_special_moves = len(comps) - 5
            special_moves = []
            for i in range(5, len(comps)):  # range goes up to but NOT including the stop index
                special_moves.append(comps[i])
            this_console.print(f'special_moves == {special_moves}')
            if comps[2] == 'i':
                if num_special_moves == 1:
                    this_console.print(f'move to make: {move_to_make},   desired response is: {special_moves}')
                else:
                    this_console.print(f'move to make: {move_to_make},   desired response is any of: {special_moves}')
            else:
                this_console.print(
                    f'move to make: {move_to_make},   desired response is any move except for: {special_moves}')

            # moves_as_list = get_full_move_list(chrome_driver)
            # move_number = len(moves_as_list) // 3 + 1
            # make the 'move to make'
            iteration_count = 1
            stop_loop = False
            inner_stop_loop = False
            # max_engine_score = '+1.00'
            cumul_dict_moves = {}  # the key is the move and the value is a count of times that that move was the result
            comp_move_num_to_get = move_num_to_make + (1 if user_color == Player_Color.BLACK else 0)
            while not stop_loop and get_key_nonblocking() != 'q':
                if move_num_to_make > 0:
                    while not inner_stop_loop:
                        try:
                            square_size = get_square_size(chrome_driver)
                            try:
                                make_move_and_promote(chrome_driver, square_size, move_to_make, white_on_top, user_color)
                                # time.sleep(0.5)
                                # moves_as_list = get_full_move_list(chrome_driver)
                                # this_console.print(f'moves_as_list right after make_move_and_promote is {moves_as_list}')
                                # move_number = len(moves_as_list) // 3 + 1
                                # time.sleep(0.1)
                                # this_console.print(f'move_number = len(moves_as_list) == {move_number}')
                                inner_stop_loop = True

                            except:
                                this_console.print('error making move', style='red on default')
                                time.sleep(1.0)
                        except:
                            this_console.print('error getting square size', style='red on default')
                            time.sleep(0.1)
                inner_stop_loop = False
                time.sleep(0.1)
                # this_console.print(f'user_color == {user_color}')
                response_move = wait_for_then_get_latest_move(chrome_driver, computer_color, comp_move_num_to_get)  # .lower()
                # time.sleep(0.1)
                # this_console.print(f'response_move == {response_move}')
                # if response_move in dict then get its index and
                # this_console.print(f'cumul_dict_moves == {cumul_dict_moves}')
                if response_move in cumul_dict_moves:
                    cumul_dict_moves[response_move] += 1
                else:
                    cumul_dict_moves[response_move] = 1
                if incl_excl == 'i':
                    if response_move in special_moves:
                        # this_console.print(2)
                        play_winning_sound()
                        stop_loop = True
                        this_console.print(
                            f'iter {iteration_count} was successful with response move of {response_move}!')
                    else:
                        this_console.print(f'iter {iteration_count}:', end=' ')
                        pretty_print_moves(cumul_dict_moves)
                        iteration_count += 1
                        # time.sleep(1.0)
                        # if iteration_count % 3 == 0:
                        #     chrome_driver.refresh()
                        #     time.sleep(1.0)
                        if move_num_to_make == 0 and user_color == Player_Color.BLACK:
                            resign_and_start_new_game(chrome_driver)
                        else:
                            click_back_button(chrome_driver)
                        # move_number -= 1
                        # time.sleep(0.5)
                else:
                    if response_move not in special_moves:
                        # this_console.print(3)
                        play_winning_sound()
                        stop_loop = True
                        this_console.print(
                            f'iter {iteration_count} was successful with response move of {response_move}!')
                    else:
                        this_console.print(f'iter {iteration_count}:', end=' ')
                        pretty_print_moves(cumul_dict_moves)
                        iteration_count += 1
                        # time.sleep(1.0)
                        # if iteration_count % 3 == 0:
                        #     chrome_driver.refresh()
                        #     time.sleep(1.0)
                        if move_num_to_make == 0 and user_color == Player_Color.BLACK:
                            resign_and_start_new_game(chrome_driver)
                        else:
                            click_back_button(chrome_driver)
                        # move_number -= 1
                        # time.sleep(0.5)
                if 0 < limit_trials < iteration_count:
                    stop_loop = True
                    play_losing_sound()
            # get the response
            # check to see if desired response
            #   if not, refresh, and go back one move
            #   if yes, play winning sound and go back to the command prompt
            # repeat

    # get_key_blocking()
    abort_program(0)


if __name__ == '__main__':
    main()
