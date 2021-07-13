from __future__ import nested_scopes
from checkers_game import *
import numpy as np
import math

cache = {} #you can use this to implement state caching!

# Method to compute utility value of terminal state
def compute_utility(state, color):

    utility = 0

    # convert board list of lists into numpy array
    board = np.array(state.board)

    pieces = ['r', 'R', 'b', 'B']

    # get the occurences of each piece in the game board
    elt, count = np.unique(board, return_counts=True)

    hash_table = dict(zip(elt, count))

    for piece in pieces:
        if piece not in hash_table.keys():
            hash_table[piece] = 0
    
    black_score = 2*hash_table['B'] + hash_table['b']
    red_score = 2*hash_table['R'] + hash_table['r']

    # calculate utility depending on color
    utility = red_score - black_score if color == 'r' else black_score - red_score

    return utility

# Better heuristic value of board
def compute_heuristic(state, color): 
    # IMPLEMENT
    return 0  # change this!


############ MINIMAX ###############################
def minimax_min_node(state, color, limit, caching=0):

    # initial best state is None
    best_state = None

    opp = 'b' if color == 'r' else 'r'

    res = np.array(state.board)
    key = hash(tuple(map(tuple, res)))

    if caching and key in cache.keys():
        return cache[key]

    # check for terminal state
    if len(successors(state, color)) == 0 or limit == 0:
        return compute_utility(state, opp), best_state

    # initial value is infinity
    value = float('inf')

    # iterate over all the successors
    for succ in successors(state, color):
        next_value, next_state = minimax_max_node(succ, opp, limit - 1, caching)

        if next_value < value:
            value, best_state = next_value, succ

    if caching and best_state is not None and key not in cache.keys():
        cache[key] = value, best_state
        
    return value, best_state


def minimax_max_node(state, color, limit, caching=0):
    
    # initial best state is None
    best_state = None

    opp = 'b' if color == 'r' else 'r'

    res = np.array(state.board)
    key = hash(tuple(map(tuple, res)))

    if caching and key in cache.keys():
        return cache[key]

    # check for terminal state
    if len(successors(state, color)) == 0 or limit == 0:
        return compute_utility(state, color), best_state

    # initial value is -infinity
    value = float('-inf')

    # iterate over all the successors
    for succ in successors(state, color):
        next_value, next_state = minimax_min_node(succ, opp, limit - 1, caching)

        if next_value > value:
            value, best_state = next_value, succ

    if caching and best_state is not None and key not in cache.keys():
        cache[key] = value, best_state

    return value, best_state


def select_move_minimax(state, color, limit, caching=0):
    """
        Given a state (of type Board) and a player color, decide on a move.
        The return value is a list of tuples [(i1,j1), (i2,j2)], where
        i1, j1 is the starting position of the piece to move
        and i2, j2 its destination.  Note that moves involving jumps will contain
        additional tuples.

        Note that other parameters are accepted by this function:
        If limit is a positive integer, your code should enforce a depth limit that is equal to the value of the parameter.
        Search only to nodes at a depth-limit equal to the limit.  If nodes at this level are non-terminal return a heuristic
        value (see compute_utility)
        If caching is ON (i.e. 1), use state caching to reduce the number of state evaluations.
        If caching is OFF (i.e. 0), do NOT use state caching to reduce the number of state evaluations.
    """
    res = minimax_max_node(state, color, limit, caching)[1].move
    if res:
        return res
    return None


############ ALPHA-BETA PRUNING #####################
def alphabeta_min_node(state, color, alpha, beta, limit, caching=0, ordering=0):

    # initial best state is None
    best_state = None

    opp = 'b' if color == 'r' else 'r'

    res = np.array(state.board)
    key = hash(tuple(map(tuple, res)))

    if caching and key in cache.keys():
        return cache[key]

    # check for terminal state
    if len(successors(state, color)) == 0 or limit == 0:
        return compute_utility(state, opp), best_state

    # initial value is infinity
    value = float('inf')

    # iterate over all the successors
    for succ in successors(state, color):
        next_value, next_state = alphabeta_max_node(succ, opp, alpha, beta, limit - 1, caching, ordering)

        if next_value < value:
            value, best_state = next_value, succ
        
        # check for pruning
        if value <= alpha:
            return value, best_state
            
        beta = min(beta, value)

    if caching and best_state is not None and key not in cache.keys():
        cache[key] = value, best_state

    return value, best_state

def alphabeta_max_node(state, color, alpha, beta, limit, caching=0, ordering=0):

    # initial best state is None
    best_state = None

    opp = 'b' if color == 'r' else 'r'

    res = np.array(state.board)
    key = hash(tuple(map(tuple, res)))

    if caching and key in cache.keys():
        return cache[key]

    # check for terminal state
    if len(successors(state, color)) == 0 or limit == 0:
        return compute_utility(state, color), best_state

    # initial value is -infinity
    value = float('-inf')

    # iterate over all the successors
    for succ in successors(state, color):
        next_value, next_state = alphabeta_min_node(succ, opp, alpha, beta, limit - 1, caching, ordering)

        if next_value > value:
            value, best_state = next_value, succ

        if value >= beta:
            return value, best_state
        
        alpha = max(alpha, value)

    if caching and best_state is not None and key not in cache.keys():
        cache[key] = value, best_state
    
    return value, best_state

def select_move_alphabeta(state, color, limit, caching=0, ordering=0):
    """
    Given a state (of type Board) and a player color, decide on a move. 
    The return value is a list of tuples [(i1,j1), (i2,j2)], where
    i1, j1 is the starting position of the piece to move
    and i2, j2 its destination.  Note that moves involving jumps will contain
    additional tuples.

    Note that other parameters are accepted by this function:
    If limit is a positive integer, your code should enforce a depth limit that is equal to the value of the parameter.
    Search only to nodes at a depth-limit equal to the limit.  If nodes at this level are non-terminal return a heuristic 
    value (see compute_utility)
    If caching is ON (i.e. 1), use state caching to reduce the number of state evaluations.
    If caching is OFF (i.e. 0), do NOT use state caching to reduce the number of state evaluations.    
    If ordering is ON (i.e. 1), use node ordering to expedite pruning and reduce the number of state evaluations. 
    If ordering is OFF (i.e. 0), do NOT use node ordering to expedite pruning and reduce the number of state evaluations. 
    """
    # IMPLEMENT
    res = alphabeta_max_node(state, color, float('-inf'), float('inf'), limit, caching, ordering)[1].move
    if res:
        return res
    return None 

# ======================== Class GameEngine =======================================
class GameEngine:
    def __init__(self, str_name):
        self.str = str_name

    def __str__(self):
        return self.str

    # The return value should be a move that is denoted by a list
    def nextMove(self, state, alphabeta, limit, caching, ordering):
        global PLAYER
        PLAYER = self.str
        if alphabeta:
            result = select_move_alphabeta(Board(state), PLAYER, limit, caching, ordering)
        else:
            result = select_move_minimax(Board(state), PLAYER, limit, caching)

        return result
