#Look for #IMPLEMENT tags in this file.
'''
All models need to return a CSP object, and a list of lists of Variable objects 
representing the board. The returned list of lists is used to access the 
solution. 

For example, after these three lines of code

    csp, var_array = futoshiki_csp_model_1(board)
    solver = BT(csp)
    solver.bt_search(prop_FC, var_ord)

var_array[0][0].get_assigned_value() should be the correct value in the top left
cell of the Futoshiki puzzle.

1. futoshiki_csp_model_1 (worth 20/100 marks)
    - A model of a Futoshiki grid built using only 
      binary not-equal constraints for both the row and column constraints.

2. futoshiki_csp_model_2 (worth 20/100 marks)
    - A model of a Futoshiki grid built using only n-ary 
      all-different constraints for both the row and column constraints. 

'''
from cspbase import *
import itertools

def get_variables(futo_grid):
    '''
    input: a list of lists representing the game futoshiki including both cells and inequalities
    return: a list of all the variables 
    '''
    variables = list()

    # get the size of the grid: nxn
    grid_size = len(futo_grid)

    col_size = 2*grid_size - 1

    # in any grid, the variables are in the even columns: 0, 2, 4,...
    for row in range(grid_size):

        for col in range(col_size, 2):

            name = "var {} {}".format(row, col)

            # if the cell at (row, col) == 0, then domain = [1,2,..n]
            # else if cell at (row, col) == x, then domain = [x]
            if futo_grid[row][col] == 0:
                domain = range(1, grid_size + 1)
            else:
                domain = [futo_grid[row][col]]

            # create the variable
            var = Variable(name, domain)

            # add variable to the list of variables
            variables.append(var)
    
    return variables

def futoshiki_csp_model_1(futo_grid):
    ##IMPLEMENT
    return None, None
    

def futoshiki_csp_model_2(futo_grid):
    ##IMPLEMENT 
    return None, None
   
