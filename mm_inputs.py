# File: mm_inputs.py
# Purpose: input-related stuff for MinMater
from csv import DictReader
import os


def read_input_file(a_console, input_file_path="auto_inputs_2.csv") -> dict:
    # returns a dictionary of all the requested runs to perform
    # the key is indexed from 1 to n
    # the value is a list containing input elements for that specific run
    if not os.path.exists(input_file_path):
        return None
    results = {}
    with open(input_file_path, mode='r') as file:
        reader = DictReader(file)
        for row in reader:
            results[row['name']] = [ row['color'], int(row['record_to_beat']), int(row['target_record']) ]
    return results


def read_focused_input_file(input_file_path="auto_focused.csv") -> dict:
    # returns a dictionary
    # the keys in order are: name,    color, record_to_beat, num_moves_to_repeat, w1, b1, w2, b2, ..., w19, b19
    # the values (corresp.): Maurice, b,     19,             5,                 , Nf3,c5,g3, Nf6, ..., Kf1, Qxf2#
    if not os.path.exists(input_file_path):
        return None
    results = {}
    with open(input_file_path, mode='r') as file:
        lines = file.readlines()
    current_row = 0
    row_vals = []
    for line in lines:
        current_row += 1
        if current_row == 1:
            continue
        if current_row == 2:
            row_vals = line.strip().split(",")
            assert(len(row_vals) == 5)
            results['name'] = row_vals[0]
            results['color'] = row_vals[1]
            results['record_to_beat'] = row_vals[2]
            results['target_record'] = row_vals[3]
            results['num_moves_to_repeat'] = row_vals[4]
            continue
        row_vals = line.strip().split(",")
        assert(len(row_vals) == 3)
        results[f"w{row_vals[0]}"] = row_vals[1].strip('+#')
        results[f"b{row_vals[0]}"] = row_vals[2].strip('+#')
    return results


def read_bot_mapping_file(input_file_path="chess_bot_mapping_2.csv") -> dict:
    if not os.path.exists(input_file_path):
        return None
    results = {}
    with open(input_file_path, mode='r') as file:
        reader = DictReader(file)
        for row in reader:
            results[str(row['name'])] = [ str(row['name-bot']), str(row['section'])]
    return results


def get_input_record(a_console) -> int:
    rec_to_beat = 0
    reprompt = '--Please enter a positive number > 2'
    while rec_to_beat <= 2:
        try:
            rec_to_beat = int(a_console.input("\nEnter the record number of moves to beat➤ "))
            if rec_to_beat <= 2:
                a_console.print(reprompt)
        except:
            a_console.print(reprompt)
    return rec_to_beat


def get_input_complete_games(a_console) -> bool:
    complete_games = a_console.input("\nDo you wish to play every game to completion? (y/[bold]N[/bold])➤ ")
    stripped_lowercase = complete_games.strip().lower()
    complete = False
    if stripped_lowercase != '':
        if stripped_lowercase[0] == 'y':
            complete = True
    if complete:
        a_console.print('-----You have selected to play [bold cyan]EVERY[/bold cyan] game to completion',
                        style='#65a4cf')
    else:
        a_console.print('-----You have selected to [bold cyan]NOT PLAY[/bold cyan] each game to completion',
                        style='#65a4cf')
    return complete


def get_input_move_time(a_console) -> float:
    move_time_seconds = a_console.input(prompt="\nEnter move time in seconds (default is [white]1.0[/white])➤ ")
    first_part = '-----You have selected a move time of '
    if move_time_seconds == " " or move_time_seconds == '':
        move_time_seconds = "1.0"
    try:
        move_time = float(move_time_seconds)
    except:
        a_console.print(first_part + '[bold cyan]1.000[/bold cyan]' + ' seconds', style='#65a4cf')
        return 1.0
    if move_time > 0.0:
        a_console.print(first_part + f'[bold cyan]{move_time:.3f}[/bold cyan]' + ' seconds', style='#65a4cf')
        return move_time
    a_console.print(first_part + '[bold cyan]1.000[/bold cyan]' + ' seconds', style='#65a4cf')
    return 1.0


def get_input_number_games(a_console) -> int:
    keep_playing = '-----You have selected to keep playing '
    play_up_to = '-----You have selected to play up to '
    bold_forever = '[bold cyan]FOREVER[/bold cyan]'
    try:
        num_games = a_console.input("\nEnter desired number of games to play➤ ")
        if num_games == '' or num_games == ' ':
            num_games_as_int = -1  # we'll treat this appropriately
            a_console.print(keep_playing + bold_forever, style='#65a4cf')
            return num_games_as_int
        num_games_as_int = int(num_games)
        if num_games_as_int > 0:
            a_console.print(play_up_to + f'[bold cyan]{num_games_as_int}[/bold cyan] games', style='#65a4cf')
            return num_games_as_int
        a_console.print(keep_playing + bold_forever, style='#65a4cf')
        return -1
    except:
        a_console.print(keep_playing + bold_forever, style='#65a4cf')
        return -1
