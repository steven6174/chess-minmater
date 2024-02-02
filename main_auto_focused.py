#!/home/steven/PycharmProjects/MinMater++/venv/bin/python3.10
import http.client
import time

# Program: MainMater++ Auto Focused Edition
# Purpose: Play chess.com games with the goal of achieving the quickest checkmates

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
# from selenium.common.exceptions import ElementClickInterceptedException

# from py_pushover_simple import pushover

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


def clean_up(driver: webdriver, engine: Engine) -> None:
    this_console.print('---> Quitting pygame')
    pygame.mixer.quit()
    pygame.quit()
    this_console.print('---> Terminating Stockfish')
    engine.terminate()
    this_console.print('---> Closing Chrome')
    close_chrome_driver(driver, is_windows)
    this_console.print('Complete\n')


def abort_program(return_val: int = 0, error_text: str = '') -> None:
    if error_text != '':
        this_console.print('\n\n' + error_text, style='bold red on black')
    this_console.print('\n\nClosing initiated')
    try:
        clean_up(chrome_driver, chess_engine)
    except NameError:  # in case program aborted before chrome_driver is defined
        pass
    time.sleep(1.0)  # to look a bit more professional
    exit(return_val)


def print_program_intro():
    this_console.print('MinMater++ Auto Focused Edition', style='bold #ffffff on #ff0000', justify='center')
    this_console.print('Copyright © [white]2023[/white]', style='#ffffff on #cf0030', justify='center')
    this_console.print('Steven Kendrick', style='italic #ffffff on #cf0030', justify='center')


def pause_no_echo() -> None:
    this_console.print('\nPress any key to continue. . .')
    get_key_blocking()


def pause_enter_no_echo() -> None:
    this_console.print('\nPress ENTER to continue. . .')
    while get_key_blocking() != '\n':
        pass


def print_game_number(game_number: int, bot_name='', index=1, entries=1) -> None:
    this_console.print(
        f'\n [bold red]{bot_name} ({index}/{entries}) [/bold red][red]<Game {str(game_number).zfill(4)}>[/red] [default on default] [/default on default]',
        style='bold red on default', end='')


def print_move_number(move_number: int) -> None:
    this_console.print(f'[grey93 on default]{str(move_number)}[/grey93 on default]', style='default on default',
                       end='.')


def extract_move(move_and_score: str) -> str:
    return move_and_score.split(' ')[0]


def extract_score(move_and_score: str) -> str:
    components = move_and_score.split(' ')
    if len(components) < 3:  # draw
        return ''
    return components[1] + ' ' + components[2]


def print_opening_and_evaluation(driver: webdriver, max_score_so_far: str):
    this_console.print(
        f'[black on dark red]╚══Opening:[/black on dark red] [default on default]{get_opening_name(driver)} --- {max_score_so_far}[/default on default]',
        style='default on default')


def pretty_print_score(score: str) -> str:
    if score == '':
        return ''
    # two formats for white winning: 'cp 282' , 'mate 9'
    # for black winning: 'cp -282', 'mate -9'
    comps = score.split(' ')
    if comps[0] == 'cp':
        centipawns = int(comps[1])
        numerical_score = (centipawns / 100.0)
        plus_minus = "+"
        if numerical_score < 0:
            plus_minus = ""  # it already has a minus
        formatted_score = plus_minus + f"{numerical_score:0.2f}"
    elif comps[0] == 'mate':
        num_moves = int(comps[1])
        plus_minus = "+"
        if num_moves < 0:
            plus_minus = "-"
        formatted_score = plus_minus + "M" + f"{num_moves:d}"
    else:
        raise Exception("the retrieved score is invalid")
    return formatted_score


def best_so_far(best_score: str, new_score: str) -> str:
    best_is_m = 'M' in best_score
    new_is_m = 'M' in new_score
    if best_is_m and new_is_m:
        best_last = int(best_score.split('M')[1])
        new_last = int(new_score.split('M')[1])
        return '+M' + str(min(best_last, new_last))
    if best_is_m and not new_is_m:
        return best_score
    if not best_is_m and new_is_m:
        return new_score
    return best_score if float(best_score) > float(new_score) else new_score


def main() -> None:
    global this_console, chrome_driver, chess_engine
    initialize()
    time.sleep(0.5)
    mapping_inputs = read_bot_mapping_file()
    auto_focused_inputs = read_focused_input_file()

    print_program_intro()

    complete_games = False
    move_time = 0.888
    num_games_to_play = -1

    chrome_driver = get_chrome_driver(is_win=is_windows)
    go_to_main_bot_selection_screen(chrome_driver)

    chess_engine = Engine(get_stockfish_path(), 99, move_time * 1000, param={"Threads": cpu_count(), "Ponder": False})

    # list_moves_current_game = []
    this_console.print('\nPress [bold cyan]<ENTER>[/bold cyan] to start, [bold cyan]Q[/bold cyan] to quit',
                       style='#65a4cf')
    if get_key_blocking().lower() == 'q':
        this_console.print('\n\nOK', style='cyan')
        abort_program(0)

    # user_color = determine_user_color(chrome_driver)
    user_color = Player_Color.WHITE if auto_focused_inputs['color'] == 'w' else Player_Color.BLACK
    # white_on_top = is_white_on_top(chrome_driver)
    white_on_top = user_color == Player_Color.BLACK

    # num_auto_entries = len(auto_focused_inputs)
    # # this_console.print(f'number of entries is {num_auto_entries}')
    # auto_bot_names = []
    # auto_user_colors = []
    # auto_recs_to_beat = []
    # auto_target_record = []
    # for line in auto_focused_inputs:
    #     auto_bot_names.append(line)
    #     auto_user_colors.append(Player_Color.WHITE if auto_focused_inputs[line][0] == 'w' else Player_Color.BLACK)
    #     auto_recs_to_beat.append(auto_focused_inputs[line][1])
    #     auto_target_record.append(auto_focused_inputs[line][2])

    auto_bot_name = auto_focused_inputs['name']
    auto_user_color = user_color
    auto_rec_to_beat = int(auto_focused_inputs['record_to_beat'])
    auto_target_record = int(auto_focused_inputs['target_record'])
    auto_num_moves_to_repeat = int(auto_focused_inputs['num_moves_to_repeat'])

    user_color = auto_user_color
    displayed_bot_name = auto_bot_name
    html_bot_name = mapping_inputs[displayed_bot_name][0]
    html_section_name = mapping_inputs[displayed_bot_name][1]
    record_to_beat = auto_rec_to_beat
    target_record = auto_target_record
    # click_new_game_button(chrome_driver)
    # select the desired bot opponent then click the Choose button
    try:
        choose_opponent_1(chrome_driver, html_section_name, html_bot_name)
    except:
        abort_program(1, f'Unable to find {displayed_bot_name}!')

    # select the desired user/player's color then start the game
    try:
        choose_opponent_2(chrome_driver, user_color)
    except:
        abort_program(1, f'Unable to select the proper color and start a new game!')

    chess_board = Board()
    num_games_played = 0
    full_move_number = 1

    if user_color == Player_Color.WHITE:
        # get the desired BLACK player moves (should be of length equal to num_moves_to_repeat)
        between_games_loop = True
        max_engine_score_so_far = '-99.00'
        while between_games_loop:
            current_chess_game = Chess_Game_With_Player_White(chrome_driver, white_on_top, chess_engine, move_time)
            within_game_loop = True
            while within_game_loop:
                if full_move_number == 1:
                    print_game_number(num_games_played + 1, displayed_bot_name, 1, 1)
                current_chess_game.update_square_size()
                white_best_move_and_score = current_chess_game.get_best_move_and_score()
                white_best_move = extract_move(white_best_move_and_score)
                engine_score = extract_score(white_best_move_and_score)
                max_engine_score_so_far = best_so_far(max_engine_score_so_far, pretty_print_score(engine_score))
                if current_chess_game.move_would_result_in_draw(white_best_move):
                    # get 2nd best move and play it instead
                    replacement_best_move_and_score = current_chess_game.get_second_best_move_and_score(
                        white_best_move)
                    white_best_move = extract_move(replacement_best_move_and_score)
                    engine_score = extract_score(replacement_best_move_and_score)
                    max_engine_score_so_far = best_so_far(max_engine_score_so_far, pretty_print_score(engine_score))

                pretty_score = pretty_print_score(engine_score)
                if full_move_number > 1:
                    if 'M' in pretty_score:
                        this_console.print(f'({pretty_score})', style='bold green', end=' ')
                    else:
                        this_console.print(f'[grey30]({pretty_score})[/grey30]', style='grey30', end=' ')
                print_move_number(full_move_number)
                this_console.print('[default on default]' +
                                   f'{current_chess_game.get_san_move(Move.from_uci(white_best_move))}' +
                                   '[/default on default]', end='')
                current_chess_game.make_move_and_promote(white_best_move)

                # at this point, either white won or the game goes on
                if current_chess_game.is_game_over():
                    # did it beat the record?
                    this_console.print(f' [green](White won after {full_move_number} moves)[/green]', style='green')
                    print_opening_and_evaluation(chrome_driver, max_engine_score_so_far)
                    if full_move_number < record_to_beat:
                        play_winning_sound()
                        save_game(chrome_driver)
                        this_console.print('\n[i]WOW! RECORD WIN![/i]', style='bold cyan')
                        this_console.print('\nThe game has been saved to your archive', style='bold cyan')
                        record_to_beat = full_move_number
                        if record_to_beat <= target_record:
                            play_winning_sound()
                            # go on to the next entry
                            between_games_loop = False
                            break
                    start_new_game(chrome_driver)
                    break

                # so the game goes on
                # but check to see if we're going to exit early by resigning and starting a new game
                if not complete_games and full_move_number == (record_to_beat - 1):
                    this_console.print(f'  [grey46](White resigned after {full_move_number} moves)[/grey46]')
                    print_opening_and_evaluation(chrome_driver, max_engine_score_so_far)
                    resign_and_start_new_game(chrome_driver)
                    break

                # wait for and get black's move
                try:
                    black_move = current_chess_game.wait_for_then_get_black_latest_move()
                except ElementNotInteractableException:
                    play_losing_sound()
                    break
                    chrome_driver.get('https://www.chess.com/play/computer')
                    time.sleep(1.0)
                    find_and_click_button(chrome_driver, f"//button[contains(.,'Choose')]")
                    time.sleep(1.0)
                    find_and_click_button(chrome_driver, f"//button[contains(.,'Play')]")
                    time.sleep(1.0)
                    # need to replay white's first move in the game
                    current_chess_game.make_move_and_promote(white_best_move)
                    black_move = current_chess_game.wait_for_then_get_black_latest_move()
                    play_winning_sound()

                san_black_move = current_chess_game.get_san_move(black_move)
                current_chess_game.update_with_black_move(black_move)
                this_console.print(f'⎵{san_black_move}', end='')

                # so now, either the game is over and black won, it's a draw, or the game continues
                # if the game is over then either black won or it's a draw
                if current_chess_game.is_game_over():
                    if current_chess_game.can_claim_draw():
                        this_console.print(f' [grey46](draw after {full_move_number} moves)[/grey46]')
                        print_opening_and_evaluation(chrome_driver, max_engine_score_so_far)
                    elif current_chess_game.is_checkmate():
                        this_console.print(f' [grey23](White lost after {full_move_number} moves)[/grey23]')
                        print_opening_and_evaluation(chrome_driver, max_engine_score_so_far)
                    else:
                        play_losing_sound()
                        save_game(chrome_driver)
                        pause_no_echo()
                        abort_program(1, 'something went wrong')
                    if num_games_played >= num_games_to_play != -1:
                        this_console.print(f' [grey46](White resigned after {full_move_number} moves)[/grey46]')
                        print_opening_and_evaluation(chrome_driver, max_engine_score_so_far)
                        play_winning_sound()
                        abort_program(0)
                    start_new_game(chrome_driver)
                    break

                # else the game goes on
                # check for a q key or p key and respond
                key = get_key_nonblocking()
                if key == 'q':
                    this_console.print('\n\nOK', style='bold cyan')
                    abort_program(0)
                # elif key == 'p':
                #     this_console.print('\n\nOK - Pausing now - Press any key to unpause\n', style='bold cyan')
                #     get_key_blocking()

                # back to beginning of loop (next move in current game)
                full_move_number += 1

            num_games_played += 1
            full_move_number = 1
            if num_games_to_play != -1 and num_games_played == num_games_to_play:
                between_games_loop = False

        # this_console.print('\n\nFINISHED!', style='bold cyan')
        # abort_program(0)
        pass

    else:  # user_color == Player_Color.BLACK
        # get the desired WHITE player moves (should be of length equal to num_moves_to_repeat)
        white_moves_to_repeat = []
        black_moves_to_make = []
        idx = 0
        while idx < int(auto_num_moves_to_repeat):
            idx += 1
            white_moves_to_repeat.append(auto_focused_inputs[f"w{idx}"])
            black_moves_to_make.append(auto_focused_inputs[f"b{idx}"])
        assert(len(white_moves_to_repeat) == auto_num_moves_to_repeat)
        between_games_loop = True
        max_engine_score_so_far = '-99.00'
        while between_games_loop:
            current_chess_game = Chess_Game_With_Player_Black(chrome_driver, white_on_top, chess_engine, move_time)
            within_game_loop = True
            while within_game_loop:
                if full_move_number == 1:
                    print_game_number(num_games_played + 1, displayed_bot_name, 1, 1)
                current_chess_game.update_square_size()
                print_move_number(full_move_number)
                # get white's move
                white_move = current_chess_game.wait_for_then_get_white_latest_move()
                san_white_move = current_chess_game.get_san_move(white_move)
                # if full_move_number == 1 then there must be an initial move to repeat and if we don't get it,
                #     then we'll have to start a new game and keep trying until it happens
                if full_move_number == 1:
                    while san_white_move != white_moves_to_repeat[0]:
                        # this_console.print('have to try again')
                        current_chess_game = Chess_Game_With_Player_Black(chrome_driver, white_on_top, chess_engine,
                                                                          move_time)
                        resign_and_start_new_game(chrome_driver)
                        white_move = current_chess_game.wait_for_then_get_white_latest_move()
                        san_white_move = current_chess_game.get_san_move(white_move)
                else:
                    if full_move_number <= auto_num_moves_to_repeat:
                        while san_white_move != white_moves_to_repeat[full_move_number-1]:
                            click_back_button(chrome_driver)
                            full_move_number -= 1
                            current_chess_game.remove_last_black_move()
                            current_chess_game.make_move_and_promote(black_moves_to_make[full_move_number-1])
                            white_move = current_chess_game.wait_for_then_get_white_latest_move()
                            san_white_move = current_chess_game.get_san_move(white_move)
                            full_move_number += 1

                current_chess_game.update_with_white_move(white_move)
                this_console.print('[default on default]' +
                                   f'{san_white_move}' +
                                   '[/default on default]', end='')

                # after white's move, either white checkmated black, it's a draw, or the game continues
                if current_chess_game.is_game_over():
                    # either white won or it's a draw
                    if current_chess_game.can_claim_draw():
                        this_console.print(f' [grey46](draw after {full_move_number} moves)[/grey46]')
                        print_opening_and_evaluation(chrome_driver, max_engine_score_so_far)
                    elif current_chess_game.is_checkmate():
                        this_console.print(f' [grey23](Black lost after {full_move_number} moves)[/grey23]')
                        print_opening_and_evaluation(chrome_driver, max_engine_score_so_far)
                    if num_games_played >= num_games_to_play != -1:
                        this_console.print(f' [grey46](Black resigned after {full_move_number} moves)[/grey46]')
                        print_opening_and_evaluation(chrome_driver, max_engine_score_so_far)
                        play_winning_sound()
                        abort_program(0)
                    start_new_game(chrome_driver)
                    break

                # the game is NOT over so either resign and move on to next game or continue this game
                if not complete_games and full_move_number == (record_to_beat - 0):
                    this_console.print(f'  [grey46](Black resigned after {full_move_number} moves)[/grey46]')
                    print_opening_and_evaluation(chrome_driver, max_engine_score_so_far)
                    time.sleep(1)
                    if num_games_played >= num_games_to_play != -1:
                        play_winning_sound()
                        abort_program(0)
                    resign_and_start_new_game(chrome_driver)
                    break
                # so the game goes on
                # check for q key and respond
                key = get_key_nonblocking()
                if key == 'q':
                    this_console.print('\n\nOK', style='bold cyan')
                    abort_program(0)
                # elif key == 'p':
                #     this_console.print('\n\nOK - Pausing now - Press any key to unpause\n', style='bold cyan')
                #     get_key_blocking()

                # get best move from engine
                current_chess_game.update_square_size()
                black_best_move_and_score = current_chess_game.get_best_move_and_score()
                black_best_move = extract_move(black_best_move_and_score)
                if full_move_number <= auto_num_moves_to_repeat:
                    black_best_move = black_moves_to_make[full_move_number-1]
                engine_score = extract_score(black_best_move_and_score)  # is not in sync now but whatever
                max_engine_score_so_far = best_so_far(max_engine_score_so_far, pretty_print_score(engine_score))
                if current_chess_game.move_would_result_in_draw(black_best_move):
                    # get 2nd best move and play it instead
                    replacement_best_move_and_score = current_chess_game.get_second_best_move_and_score(
                        black_best_move)
                    black_best_move = extract_move(replacement_best_move_and_score)
                    engine_score = extract_score(replacement_best_move_and_score)
                    max_engine_score_so_far = best_so_far(max_engine_score_so_far, pretty_print_score(engine_score))

                san_black_move = current_chess_game.get_san_move(Move.from_uci(black_best_move))
                current_chess_game.make_move_and_promote(black_best_move)
                # current_chess_game.update_with_black_move(black_best_move)
                this_console.print(f'[default on default]⎵{san_black_move}[/default on default]', end='')

                pretty_score = pretty_print_score(engine_score)
                if 'M' in pretty_score:
                    this_console.print(f'({pretty_score})', style='bold green', end=' ')
                else:
                    this_console.print(f'[grey30]({pretty_score})[/grey30]', style='grey30', end=' ')
                time.sleep(0.25)  # wait for move to be manifested in html, possible to reduce?

                # at this point, either black has won or the game goes on
                if current_chess_game.is_game_over():
                    # did it beat the record?
                    this_console.print(f' [green](Black won after {full_move_number} moves)[/green]', style='green')
                    print_opening_and_evaluation(chrome_driver, max_engine_score_so_far)
                    if full_move_number < record_to_beat:
                        play_winning_sound()
                        save_game(chrome_driver)
                        this_console.print('\n[i]WOW! RECORD WIN![/i]', style='bold cyan')
                        this_console.print('\nThe game has been saved to your archive', style='bold cyan')

                        #p = pushover.Pushover()
                        #p.user = 'u8n6jgf7o7cmrp3hqgccketo3yzvr8'
                        #p.token = 'a238k1itun6srze21gsnk24jofo366'
                        #p.send_message(f'From Desktop: Record beat against {displayed_bot_name} playing as black. Won in only {full_move_number} moves!')

                        record_to_beat = full_move_number  # try to improve on the record
                        if record_to_beat <= target_record:
                            play_winning_sound()
                            # go on to the next entry
                            between_games_loop = False
                            break
                    start_new_game(chrome_driver)
                    break

                numerical_engine_score = 99 if 'M' in pretty_score else float(pretty_score)
                # if (not complete_games and full_move_number == (record_to_beat - 1)) or \
                #         (full_move_number > int(record_to_beat/2.5) and not complete_games and numerical_engine_score < 1.0 ):
                #     this_console.print(f'  [grey46](Black resigned after {full_move_number} moves)[/grey46]')
                #     print_opening_and_evaluation(chrome_driver, max_engine_score_so_far)
                #     resign_and_start_new_game(chrome_driver)
                #     break

                # so the game continues, and we go through the loop again
                full_move_number += 1

            num_games_played += 1
            full_move_number = 1
            if num_games_to_play != -1 and num_games_played == num_games_to_play:
                between_games_loop = False
        pass
        # this_console.print('\n\nFINISHED!', style='bold cyan')
        # abort_program(0)
    pass
    abort_program(0)


if __name__ == '__main__':
    main()
