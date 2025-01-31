import copy
import json
import random
import sys
import State

from getmac import get_mac_address as gma


class GameInformation:

    @staticmethod
    def create_game_info(game_fen: str):
        base_info = {
            'fen': game_fen,    # The game board, whose turn is it, other information
            'p1': gma(),        # Identification of machine 1
            'p2': None,         # Identification of machine 2
            'w': None,          # Which player is assigned to this role
            'b': None,          # Which player is assigned to this role
            'status': State.ONGOING,    # Game status (FF, ONGOING, FINISHED, CHEATED)
            'win': None,        # Assigning of p1 or p2
            'lose': None,       # Assigning of p1 or p2
            'seq': -1           # Sequence number
        }
        return GameInformation(base_info)

    def __init__(self, info: dict):
        self.__can_i_update = True
        self.__info = info

        self.__fen = info['fen']
        self.__p1 = info['p1']
        self.__p2 = info['p2']
        self.__w = info['w']
        self.__b = info['b']
        self.__status = info['status']
        self.__win = info['win']
        self.__lose = info['lose']
        self.__seq = info['seq']

        self.__this_user_mac = gma()

    def get_player(self, key: str) -> str:
        p = self.__w if key == 'w' else self.__b if key == 'b' else None
        return p

    def get_fen(self) -> str:
        return self.__fen

    def set_fen(self, fen: str):
        self.__fen = fen

    def get_dic(self) -> dict:
        return self.assemble()

    def game_is_initiated(self) -> bool:
        if not self.p2_exists():
            if self.__p1 == self.get_mac():
                print('You are already player1. Wait for player 2...')
                self.__can_i_update = False
                return False

            while True:
                inp = input('There is no 2nd player, would you like to play? (y/n)')
                if inp == 'y':
                    self.set_p2(gma())
                    break
                elif inp == 'n':
                    sys.exit(0)
                else:
                    pass

            self.assign_roles()

            color = 'White' if self.__w == 'p2' else 'Black'
            print('Assigning roles, you are %s' % color)
            self.inc_seq()
            return False
        else:
            print('Game is loading..')
            return True

    def can_i_update(self):
        return self.__can_i_update

    def p2_exists(self):
        return self.__p2 is not None

    def set_p1(self, pid: str):
        self.__p1 = pid

    def set_p2(self, pid: str):
        self.__p2 = pid

    def inc_seq(self):
        self.__seq += 1

    def assign_roles(self):
        roles = random.randint(0, 1)
        if roles:
            self.__w = 'p1'
            self.__b = 'p2'
        else:
            self.__w = 'p2'
            self.__b = 'p1'

    def get_mac(self):
        return self.__this_user_mac

    def assemble(self) -> dict:
        self.__info['fen'] = self.__fen
        self.__info['p1'] = self.__p1
        self.__info['p2'] = self.__p2
        self.__info['w'] = self.__w
        self.__info['b'] = self.__b
        self.__info['status'] = self.__status
        self.__info['win'] = self.__win
        self.__info['lose'] = self.__lose
        self.__info['seq'] = self.__seq
        return self.__info

    def assigned(self):
        return self.__w is not None and self.__b is not None

    def __str__(self):
        return json.dumps(self.assemble())

    def set_status(self, status: str):
        self.__status = status

    def set_ff(self, param):
        pass

    def set_winner(self, winner: str):
        self.__win = winner

    def set_loser(self, loser: str):
        self.__lose = loser

    def get_status(self) -> str:
        return self.__status

    def get_winner(self) -> str:
        return self.__win

    def get_loser(self):
        return self.__lose

    def get_seq(self) -> int:
        return self.__seq
