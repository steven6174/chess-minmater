from chess import Board, Move
from mm_enums import Player_Color
from selenium import webdriver
from mm_chrome import *
from mm_chess_engine import Engine, get_best_move, get_second_best_move
import time


# encapsulates a collection of chess games
class Chess_Games:
    pass


class Chess_Game_With_Player_White:
    _current_board: Board
    _player_color: Player_Color
    _player_on_top: bool
    _white_on_top: bool
    _list_made_moves: []  # for both white and black
    _driver: webdriver
    _engine: Engine
    _move_time: float  # in seconds
    _square_size: float
    _full_move_number: int

    def __init__(self, driver: webdriver, white_on_top: bool, engine: Engine, move_time: float):
        self._current_board = Board()
        self._player_color = Player_Color.WHITE
        self._player_on_top = white_on_top
        self._white_on_top = white_on_top
        self._list_made_moves = []  # want this to be in SAN form
        self._driver = driver
        self._engine = engine
        self._move_time = move_time
        self._full_move_number = 1

    def update_square_size(self) -> None:
        self._square_size = get_square_size(self._driver)

    def get_best_move_and_score(self):
        self._engine.setposition(self._current_board.fen())
        return get_best_move(self._engine, self._current_board, self._move_time)

    def get_second_best_move_and_score(self, initial_best_move: str):
        self._engine.setposition(self._current_board.fen())
        return get_second_best_move(self._engine, self._current_board, self._move_time, initial_best_move)

    def move_would_result_in_draw(self, move_to_test: str) -> bool:
        self._current_board.push(Move.from_uci(move_to_test))
        would_be_draw = self._current_board.can_claim_draw()
        self._current_board.pop()
        return would_be_draw

    def make_move_and_promote(self, move: str):
        make_move_and_promote(self._driver, self._square_size, move, self._white_on_top, self._player_color)
        move_san = self._current_board.san(real_move := Move.from_uci(move))
        self._current_board.push(real_move)
        self._list_made_moves.append(move_san)
        time.sleep(0.25)  # wait for move to be manifested in html, try reducing?

    def is_game_over(self) -> bool:
        return self._current_board.is_game_over()

    def wait_for_then_get_black_latest_move(self):
        return wait_for_then_get_black_latest_move(self._driver, self._current_board, self._full_move_number)

    def update_with_black_move(self, move: Move):
        move_san = self._current_board.san(move)
        self._current_board.push(move)
        self._list_made_moves.append(move_san)
        self._full_move_number += 1

    def get_san_move(self, move: Move) -> str:
        return self._current_board.san(move)

    def can_claim_draw(self) -> bool:
        return self._current_board.can_claim_draw()

    def is_checkmate(self) -> bool:
        return self._current_board.is_checkmate()


class Chess_Game_With_Player_Black:
    _current_board: Board
    _player_color: Player_Color
    _player_on_top: bool
    _white_on_top: bool
    _list_made_moves: []  # for both white and black
    _driver: webdriver
    _engine: Engine
    _move_time: float  # in seconds
    _square_size: float
    _full_move_number: int

    def __init__(self, driver: webdriver, white_on_top: bool, engine: Engine, move_time: float):
        self._current_board = Board()
        self._player_color = Player_Color.BLACK
        self._player_on_top = not white_on_top
        self._white_on_top = white_on_top
        self._list_made_moves = []  # want this to be in SAN form
        self._driver = driver
        self._engine = engine
        self._move_time = move_time
        self._full_move_number = 0

    def update_square_size(self) -> None:
        self._square_size = get_square_size(self._driver)

    def get_best_move_and_score(self):
        self._engine.setposition(self._current_board.fen())
        return get_best_move(self._engine, self._current_board, self._move_time)

    def get_second_best_move_and_score(self, initial_best_move: str):
        self._engine.setposition(self._current_board.fen())
        return get_second_best_move(self._engine, self._current_board, self._move_time, initial_best_move)

    def move_would_result_in_draw(self, move_to_test: str) -> bool:
        self._current_board.push(Move.from_uci(move_to_test))
        would_be_draw = self._current_board.can_claim_draw()
        self._current_board.pop()
        return would_be_draw

    def remove_last_black_move(self):
        self._current_board.pop()
        self._list_made_moves.pop()
        self._full_move_number -= 1
        assert(self._full_move_number >= 1)
        time.sleep(0.25)

    def make_move_and_promote(self, move: str):
        make_move_and_promote(self._driver, self._square_size, move, self._white_on_top, self._player_color)
        move_san = self._current_board.san(real_move := Move.from_uci(move))
        self._current_board.push(real_move)
        self._list_made_moves.append(move_san)
        time.sleep(0.25)  # wait for move to be manifested in html, try reducing?

    def is_game_over(self) -> bool:
        return self._current_board.is_game_over()

    def wait_for_then_get_white_latest_move(self):
        self._full_move_number += 1
        return wait_for_then_get_white_latest_move(self._driver, self._current_board, self._full_move_number)

    def update_with_white_move(self, move: Move):
        move_san = self._current_board.san(move)
        self._current_board.push(move)
        self._list_made_moves.append(move_san)

    def get_san_move(self, move: Move) -> str:
        return self._current_board.san(move)

    def can_claim_draw(self) -> bool:
        return self._current_board.can_claim_draw()

    def is_checkmate(self) -> bool:
        return self._current_board.is_checkmate()
