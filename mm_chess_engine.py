"""
    Simple Python Stockfish UCI wrapper
    expanded by Steven Kendrick
    UCI chess engine https://www.stockfishchess.com/
    :copyright: (c) 2016 by Dani Korniliev
    :license: GNU General Public License, see LICENSE for more details.
"""
import subprocess

import chess
from glob import glob
from mm_misc import is_windows
from os import cpu_count
import re
from sys import exit


def get_stockfish_path() -> str:
    if is_windows():
        for file in glob(".\\engine\\stockfish_*.exe"):
            return file
    else:
        for file in glob("/home/steven/PycharmProjects/MinMater++/engine/stockfish_*"):
            return file
    raise FileNotFoundError('Stockfish engine file not found')


# noinspection GrazieInspection,PyInitNewSignature,PyDefaultArgument,PyArgumentList,RegExpRedundantEscape,RegExpDuplicateCharacterInClass
class Engine(subprocess.Popen):
    """
        Initiates Stockfish Chess Engine with default param
    """

    def __init__(self, engine_path='', depth=99, movetime=100, param={}):
        """

        :param engine_path: where Stockfish file is located
        :param depth: the depth in plies to search
        :param movetime: the number of milliseconds to allocate for determining best move
        :param param: other parameters such as Threads, Ponder, etc.
        """
        subprocess.Popen.__init__(self, engine_path, universal_newlines=True,
                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        stockfish_default_param = {
            "Debug Log File": "engine_debug.log",  # type string default
            # Threads type spin default 1 min 1 max 512 <--- this gets passed in through 'param'
            # Hash type spin default 16 min 1 max 33554432
            # Clear Hash type button
            "Ponder": False,  # type check default false
            # MultiPV type spin default 1 min 1 max 500
            # Skill Level type spin default 20 min 0 max 20
            # Move Overhead type spin default 10 min 0 max 5000
            # Slow Mover type spin default 100 min 10 max 1000
            # nodestime type spin default 0 min 0 max 10000
            # UCI_Chess960 type check default false
            # UCI_AnalyseMode type check default false
            # UCI_LimitStrength type check default false
            # UCI_Elo type spin default 1350 min 1350 max 2850
            # UCI_ShowWDL type check default false
            # SyzygyPath type string default <empty>
            # SyzygyProbeDepth type spin default 1 min 1 max 100
            # Syzygy50MoveRule type check default true
            # SyzygyProbeLimit type spin default 7 min 0 max 7
            "Use NNUE": True,  # type check default true
            # "EvalFile": "nn-6877cd24400e.nnue"  # type string default nn-6877cd24400e.nnue
        }

        default_param = stockfish_default_param

        default_param.update(param)
        self.param = default_param
        for name, value in list(default_param.items()):
            self.setoption(name, value)

        self.uci()
        self.depth = str(depth)
        self.movetime = str(movetime)

    def send(self, command):
        self.stdin.write(command + '\n')
        self.stdin.flush()

    def flush(self):
        self.stdout.flush()

    def uci(self):
        self.send('uci')
        while True:
            line = self.stdout.readline().strip()
            if line == 'uciok':
                return line

    def setoption(self, optionname, value):
        """ Update default_param dict """
        self.send('setoption name %s value %s' % (optionname, str(value)))
        stdout = self.isready()
        if stdout.find('No such') >= 0:
            print("stockfish was unable to set option %s" % optionname)

    def setposition(self, position):
        """
        The move format is in long algebraic notation.
        Takes list of stirngs = ['e2e4', 'd7d5']
        OR
        FEN = 'rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1'
        """
        try:
            if isinstance(position, list):
                self.send('position startpos moves {}'.format(
                    self.__listtostring(position)))
                self.isready()
            elif re.match(
                    '\s*^(((?:[rnbqkpRNBQKP1-8]+\/){7})[rnbqkpRNBQKP1-8]+)\s([b|w])\s([K|Q|k|q|-]{1,4})\s(-|[a-h]['
                    '1-8])\s(\d+\s\d+)$',
                    position):
                regexList = re.match(
                    '\s*^(((?:[rnbqkpRNBQKP1-8]+\/){7})[rnbqkpRNBQKP1-8]+)\s([b|w])\s([K|Q|k|q|-]{1,4})\s(-|[a-h]['
                    '1-8])\s(\d+\s\d+)$',
                    position).groups()
                fen = regexList[0].split("/")
                if len(fen) != 8:
                    raise ValueError("expected 8 rows in position part of fen: {0}".format(repr(fen)))

                for fenPart in fen:
                    field_sum = 0
                    previous_was_digit, previous_was_piece = False, False

                    for c in fenPart:
                        if c in ["1", "2", "3", "4", "5", "6", "7", "8"]:
                            if previous_was_digit:
                                raise ValueError("two subsequent digits in position part of fen: {0}".format(repr(fen)))
                            field_sum += int(c)
                            previous_was_digit = True
                            previous_was_piece = False
                        elif c == "~":
                            if not previous_was_piece:
                                raise ValueError("~ not after piece in position part of fen: {0}".format(repr(fen)))
                            previous_was_digit, previous_was_piece = False, False
                        elif c.lower() in ["p", "n", "b", "r", "q", "k"]:
                            field_sum += 1
                            previous_was_digit = False
                            previous_was_piece = True
                        else:
                            raise ValueError("invalid character in position part of fen: {0}".format(repr(fen)))

                    if field_sum != 8:
                        raise ValueError("expected 8 columns per row in position part of fen: {0}".format(repr(fen)))
                self.send('position fen {}'.format(position))
                self.isready()
            else:
                raise ValueError(
                    "fen doesn`t match follow this example: rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1 ")

        except ValueError as e:
            print('\nCheck position correctness\n')
            exit(e.args)

    @staticmethod
    def __listtostring(move):
        return ' '.join(move).strip()

    def go(self):
        self.send('setoption name MultiPV value 1')
        self.send('go depth {0} movetime {1}'.format(self.depth, self.movetime))
        # self.send('go depth {0}'.format(self.depth))

    def go_with_multipv_2(self):
        self.send('setoption name MultiPV value 2')
        self.send('go depth {0} movetime {1}'.format(self.depth, self.movetime))
        # self.send('go depth {0}'.format(self.depth))

    def isready(self):
        self.send('isready')
        times_checked = 0
        while True and times_checked < 1000:
            line = self.stdout.readline().strip()
            if line == 'readyok':
                return line
            times_checked += 1
        raise TimeoutError("Engine seems to have stopped.")

    def ucinewgame(self):
        self.send('ucinewgame')
        self.isready()

    # sometimes we want to avoid a draw by repetition, and so we need the second-best move
    def second_best_move(self, initial_best: str):
        self.go_with_multipv_2()
        times_checked = 0
        # we want the value for score, too, which comes through in the output lines that start with info
        # we want the last one to return
        score_1 = ''
        score_2 = ''
        multipv_1 = ''
        multipv_2 = ''
        while True and times_checked < 3000:
            line = self.stdout.readline().strip().split(' ')
            if line[0] == 'bestmove':
                if multipv_1 != initial_best:
                    second_best = multipv_1
                    score = score_1
                else:
                    second_best = multipv_2
                    score = score_2
                return {'bestmove': second_best, 'ponder': None, 'info': score}
            elif line[0] == 'info' and len(line) >= 20:
                if line[5] == 'multipv':
                    if line[6] == '2':
                        if line[18] == 'pv':
                            score_2 = line[8] + " " + line[9]
                            multipv_2 = line[19]
                    elif line[6] == '1':
                        if line[18] == 'pv':
                            score_1 = line[8] + " " + line[9]
                            multipv_1 = line[19]
            else:
                times_checked += 1
        raise TimeoutError("Engine seems to have stopped.")

    def bestmove(self):
        self.go()
        times_checked = 0
        # we want the value for score, too, which comes through in the output lines that start with info
        # we want the last one to return
        score = ""
        while True and times_checked < 3000:
            line = self.stdout.readline().strip().split(' ')
            if line[0] == 'bestmove':
                if self.param['Ponder'] == 'true':
                    ponder = line[3]
                else:
                    ponder = None
                return {'bestmove': line[1], 'ponder': ponder, 'info': score}
            elif line[0] == 'info' and len(line) >= 10:
                if line[7] == 'score':
                    score = line[8] + " " + line[9]
            else:
                times_checked += 1
        raise TimeoutError("Engine seems to have stopped.")


# noinspection PyTypeChecker
def get_best_move(engine: Engine, board: chess.Board, move_time: float):
    while True:
        move = {'bestmove': '', 'ponder': '', 'info': ''}
        try:
            move = engine.bestmove()
        except TimeoutError:
            # restart the engine
            engine = Engine(get_stockfish_path(), 99, int(move_time * 1000),
                            param={"Threads": cpu_count()})
            engine.ucinewgame()
            engine.setposition(board.fen())
        if move["bestmove"] is not None:
            return move["bestmove"] + " " + move["info"]


# noinspection PyTypeChecker
def get_second_best_move(engine: Engine, board: chess.Board, move_time: float, initial_best_move: str):
    while True:
        move = {'bestmove': '', 'ponder': '', 'info': ''}
        try:
            move = engine.second_best_move(initial_best_move)
        except TimeoutError:
            # restart the engine
            engine = Engine(get_stockfish_path(), 99, int(move_time * 1000),
                            param={"Threads": cpu_count(), "MultiPV": 2})
            engine.ucinewgame()
            engine.setposition(board.fen())
        if move["bestmove"] is not None:
            return move["bestmove"] + " " + move["info"]
