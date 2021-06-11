#   Look for #IMPLEMENT tags in this file. These tags indicate what has
#   to be implemented to complete the warehouse domain.

#   You may add only standard python imports---i.e., ones that are automatically
#   available on TEACH.CS
#   You may not remove any imports.
#   You may not import or otherwise source any of your own files

import os #for time functions
import numpy as np
from search import * #for search engines
from sokoban import SokobanState, Direction, PROBLEMS #for Sokoban specific classes and problems
import math

def sokoban_goal_state(state):
  '''
  @return: Whether all boxes are stored.
  '''
  for box in state.boxes:
    if box not in state.storage:
      return False
  return True

def find_manhattan_distance(source, destination):
      '''
      @param source: tuple (x1, y1) representing the position of the start point
      @param destination: tuple (x2, y2) representing the position of the end point

      manhattan distance = abs(x2 - x1) + abs(y2 - y1)
      '''
      return math.fabs(destination[0] - source[0]) + math.fabs(destination[1] - source[1])

def heur_manhattan_distance(state):
#IMPLEMENT
    '''admissible sokoban puzzle heuristic: manhattan distance'''
    '''INPUT: a sokoban state'''
    '''OUTPUT: a numeric value that serves as an estimate of the distance of the state to the goal.'''
    #We want an admissible heuristic, which is an optimistic heuristic.
    #It must never overestimate the cost to get from the current state to the goal.
    #The sum of the Manhattan distances between each box that has yet to be stored and the storage point nearest to it is such a heuristic.
    #When calculating distances, assume there are no obstacles on the grid.
    #You should implement this heuristic function exactly, even if it is tempting to improve it.
    #Your function should return a numeric value; this is the estimate of the distance to the goal.

    # IMPLEMENTATION
    '''
    @param state: a SokobanState object which represents an instance of the game 
    Explanation: The heuristic is a numeric measure of how close the current state of the game,
                  in this case, state, is to the goal where all boxes are in a storage spot
    '''

    manhattan_dist = 0.0
    storage_distances = list()

    # for each box in the game state, find the closest storage site
    for box in state.boxes:
      for storage in state.storage:
        # add each distance from a box to a storage site to a list
        storage_distances.append(find_manhattan_distance(box, storage))
      
      # add the minimum distance 
      manhattan_dist += min(storage_distances)
      # clear the list to contain new distances of another box from storage sites
      storage_distances.clear()
    
    return manhattan_dist
          
#SOKOBAN HEURISTICS
def trivial_heuristic(state):
  '''trivial admissible sokoban heuristic'''
  '''INPUT: a sokoban state'''
  '''OUTPUT: a numeric value that serves as an estimate of the distance of the state (# of moves required to get) to the goal.'''
  count = 0
  for box in state.boxes:
    if box not in state.storage:
        count += 1
  return count
     

def heur_alternate(state):
#IMPLEMENT
    '''a better heuristic'''
    '''INPUT: a sokoban state'''
    '''OUTPUT: a numeric value that serves as an estimate of the distance of the state to the goal.'''
    #heur_manhattan_distance has flaws.
    #Write a heuristic function that improves upon heur_manhattan_distance to estimate distance between the current state and the goal.
    #Your function should return a numeric value for the estimate of the distance to the goal.

    hval = 0
    boxes = set(state.boxes)
    storage = set(state.storage)
    obstacles = set(state.obstacles)
    taken_storage = set()

    unstored_boxes, available_storage = [box for box in boxes if box not in storage], [spot for spot in storage if spot not in boxes]
    unstored_boxes = set(unstored_boxes)
    available_storage = set(available_storage)

    corners = [(0, 0), (state.width - 1, 0), (0, state.height - 1), (state.width - 1, state.height - 1)]

    # DEADLOCK 1: check if any unstored box is in a corner
    in_corner = any((True for elt in unstored_boxes if elt in corners))
    if in_corner: return math.inf

    # check for other DEADLOCKS
    for box in unstored_boxes:
          # Get the box position
          x_box = box[0]  # Xbox sucks except Xbox X
          y_box = box[1]

          # DEADLOCK 2: if a box is at an edge against another box or obstacle
          if x_box == 0 or x_box == state.width - 1:
                if (x_box, y_box - 1) in obstacles or (x_box, y_box + 1) in obstacles: return math.inf
                if (x_box, y_box - 1) in (unstored_boxes - set(box)) or (x_box, y_box + 1) in (unstored_boxes - set(box)):
                      return math.inf
          elif y_box == 0 or y_box == state.height - 1:
                if (x_box - 1, y_box) in obstacles or (x_box + 1, y_box) in obstacles: return math.inf
                if (x_box - 1, y_box) in (unstored_boxes - set(box)) or (x_box + 1, y_box) in (unstored_boxes - set(box)):
                      return math.inf
          
          # DEADLOCK 3: check if box is at an edge but spot is not at the edge
          # left edge
          if x_box == 0:
              spot_left_edge = any((True for obs in obstacles if obs[0] == 0))
              if not spot_left_edge: return math.inf
          # right edge
          elif x_box == state.width - 1:
              spot_right_edge = any((True for obs in obstacles if obs[0] == state.width - 1))
              if not spot_right_edge: return math.inf
          # top edge
          elif y_box == 0:
              spot_top_edge = any((True for obs in obstacles if obs[1] == 0))
              if not spot_top_edge: return math.inf
          # bottom edge
          elif y_box == state.height - 1:
              spot_bottom_edge = any((True for obs in obstacles if obs[1] == state.height - 1))
              if not spot_bottom_edge: return math.inf
          
          # DEADLOCK 4: check if box is blocked by 2 other boxes or obstacles
          # left and bottom
          if (x_box - 1, y_box) in unstored_boxes.union(obstacles) and (x_box, y_box + 1) in unstored_boxes.union(obstacles):
                return math.inf
          
          # left and top
          elif (x_box - 1, y_box) in unstored_boxes.union(obstacles) and (x_box, y_box - 1) in unstored_boxes.union(obstacles):
                return math.inf
          
          # right and bottom
          elif (x_box + 1, y_box) in unstored_boxes.union(obstacles) and (x_box, y_box + 1) in unstored_boxes.union(obstacles):
              return math.inf
          
          # right and top
          elif (x_box + 1, y_box) in unstored_boxes.union(obstacles) and (x_box, y_box - 1) in unstored_boxes.union(obstacles):
              return math.inf

    distance_storage= dict()
    distance_robot = list()
    # calculate hval now that DEADLOCK checks are completed
    for box in unstored_boxes:
          # get box poition (x,y)
          x_box, y_box = box[0], box[1]

          # iterate over all available storage
          for spot in available_storage:
                if spot not in taken_storage:
                    distance_storage[spot] = find_manhattan_distance(box, spot)
          
          # get the min key
          min_key = min(distance_storage.keys(), key=(lambda k: distance_storage[k]))

          # the min key is now a taken storage
          taken_storage.add(min_key)

          # add to hval 
          hval += distance_storage[min_key]

          # now find the closest robot
          for robot in state.robots:
                distance_robot.append(find_manhattan_distance(box, robot))
          
          # get the min distance of box to a robot and add to hval
          hval += min(distance_robot)

          # clear distance_storage and distance_robot for the next box
          distance_robot = []
          distance_storage = {}

    return hval
                

def heur_zero(state):
    '''Zero Heuristic can be used to make A* search perform uniform cost search'''
    return 0

def fval_function(sN, weight):
#IMPLEMENT
    """
    Provide a custom formula for f-value computation for Anytime Weighted A star.
    Returns the fval of the state contained in the sNode.
    Use this function stub to encode the standard form of weighted A* (i.e. g + w*h)

    @param sNode sN: A search node (containing a SokobanState)
    @param float weight: Weight given by Anytime Weighted A star
    @rtype: float
    """
  
    #Many searches will explore nodes (or states) that are ordered by their f-value.
    #For UCS, the fvalue is the same as the gval of the state. For best-first search, the fvalue is the hval of the state.
    #You can use this function to create an alternate f-value for states; this must be a function of the state and the weight.
    #The function must return a numeric f-value.
    #The value will determine your state's position on the Frontier list during a 'custom' search.
    #You must initialize your search engine object as a 'custom' search engine if you supply a custom fval function.
    return 0

def fval_function_XUP(sN, weight):
#IMPLEMENT
    """
    Another custom formula for f-value computation for Anytime Weighted A star.
    Returns the fval of the state contained in the sNode.
    Use this function stub to encode the XUP form of weighted A* 

    @param sNode sN: A search node (containing a SokobanState)
    @param float weight: Weight given by Anytime Weighted A star
    @rtype: float
    """
    return 0

def fval_function_XDP(sN, weight):
#IMPLEMENT
    """
    A third custom formula for f-value computation for Anytime Weighted A star.
    Returns the fval of the state contained in the sNode.
    Use this function stub to encode the XDP form of weighted A* 

    @param sNode sN: A search node (containing a SokobanState)
    @param float weight: Weight given by Anytime Weighted A star
    @rtype: float
    """
    return 0

def compare_weighted_astars():
#IMPLEMENT
    '''Compares various different implementations of A* that use different f-value functions'''
    '''INPUT: None'''
    '''OUTPUT: None'''
    """
    This function should generate a CSV file (comparison.csv) that contains statistics from
    4 varieties of A* search on 3 practice problems.  The four varieties of A* are as follows:
    Standard A* (Variant #1), Weighted A*  (Variant #2),  Weighted A* XUP (Variant #3) and Weighted A* XDP  (Variant #4).  
    Format each line in your your output CSV file as follows:

    A,B,C,D,E,F

    where
    A is the number of the problem being solved (0,1 or 2)
    B is the A* variant being used (1,2,3 or 4)
    C is the weight being used (2,3,4 or 5)
    D is the number of paths extracted from the Frontier (or expanded) during the search
    E is the number of paths generated by the successor function during the search
    F is the overall solution cost    

    Note that you will submit your CSV file (comparison.csv) with your code
    """

    for i in range(0,3):
        problem = PROBLEMS[i] 
        for weight in [2,3,4,5]:
          #you can write code in here if you like
          pass

def anytime_weighted_astar(initial_state, heur_fn, weight=1., timebound = 10):
#IMPLEMENT
  '''Provides an implementation of anytime weighted a-star, as described in the HW1 handout'''
  '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
  '''OUTPUT: A goal state (if a goal is found), else False'''
  '''implementation of weighted astar algorithm'''

  return False

def anytime_gbfs(initial_state, heur_fn, timebound = 10):
#IMPLEMENT
  '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
  '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
  '''OUTPUT: A goal state (if a goal is found), else False'''
  '''implementation of anytime greedy best-first search'''
  return False
