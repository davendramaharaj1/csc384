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
from itertools import combinations, product
import numpy as np

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

        for col in range(0, col_size, 2):

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

def get_binary_constraints(csp, array, name):
    # iterate over every row to get the row constraint
    for row in array:
        # get all the binary constrains for row
        for var1, var2 in list(combinations(row, 2)):
            # get the scope for this row constraint
            scope = [var1, var2]

            # get the satisfying tuples
            sat_tuple = list()
            sat_tuple = [(x, y) for x in var1.cur_domain() for y in var2.cur_domain() if x != y]

            # create the constraint
            constraint = Constraint(name=name, scope=scope)

            # add the satisfying tuples
            constraint.add_satisfying_tuples(sat_tuple)

            # add constraint to csp
            csp.add_constraint(c=constraint)

def get_inequality_constraints(csp, array, grid):
   # make grid a numpy array
   grid_array = np.array(grid)

   # get the positions of '<'
   x1, y1 = np.where(grid_array == '<')
   less_than = list(zip(x1, y1))

   # get the positions of '>'
   x2, y2 = np.where(grid_array == '>')
   greater_than = list(zip(x2, y2))

   # less than constraints
   name = 'less than constraint'
   for x, y in less_than:
       var1 = array[x][(y - 1)//2]
       var2 = array[x][(y + 1)//2]
       scope = [var1, var2]

       sat_tuples = list()
       sat_tuples = [(i, j) for i in var1.cur_domain() for j in var2.cur_domain() if i < j]

       # create constraint
       constraint = Constraint(name=name, scope=scope)

       # add satisfying tuple
       constraint.add_satisfying_tuples(sat_tuples)

       # add constraint
       csp.add_constraint(constraint)
    
    # greater than constraints
   name = 'greater than constraint'
   for x, y in greater_than:
       var1 = array[x][(y - 1)//2]
       var2 = array[x][(y + 1)//2]
       scope = [var1, var2]

       sat_tuples = list()
       sat_tuples = [(i, j) for i in var1.cur_domain() for j in var2.cur_domain() if i > j]

       # create constraint
       constraint = Constraint(name=name, scope=scope)

       # add satisfying tuple
       constraint.add_satisfying_tuples(sat_tuples)

       # add constraint
       csp.add_constraint(constraint)

def get_all_different_constraints(csp, array, name):
    # number of elements per row
    N = len(array)

    # iterate over every row 
    for row in array:
        scope = list()
        all_domains = list()
        sat_tuples = list()

        # create a 2D list of the curr domain of each variable in this row
        all_domains = [var.cur_domain() for var in row]

        # scope of this constraint is the row
        scope = row

        # get all possible permutations of N lists in all_domains
        sat_tuples = [perm for perm in list(product(*all_domains)) if len(set(perm)) == N]

        # create the constraint
        constraint = Constraint(name=name, scope=scope)

        # add the satisfying tuples
        constraint.add_satisfying_tuples(sat_tuples)

        # add constraint to csp
        csp.add_constraint(c=constraint)

def futoshiki_csp_model_1(futo_grid):
    '''
    Uses binary constraints by taking the combinations of 2 of each row and each column
    '''
    # extract the variables from the grid
    var_list = get_variables(futo_grid)

    # make an nxn numpy array of the variable list
    size = len(futo_grid)
    futo_array = np.array(var_list).reshape(-1, size)

    # create a csp object 
    model1 = CSP(name='Model 1', vars=var_list)

    # get the binary constraints for row
    get_binary_constraints(model1, futo_array, name='a row constraint')

    # get binary constraints for a column
    array_transposed = futo_array.transpose()
    get_binary_constraints(model1, array_transposed, name='a col constraint')

    # get the inequality constraints
    get_inequality_constraints(model1, futo_array, futo_grid)

    return model1, futo_array.tolist()
    
def futoshiki_csp_model_2(futo_grid):
    '''
    Uses all_different constraints for each row and  column
    '''
    # extract the variables from the grid
    var_list = get_variables(futo_grid)

    # make an nxn numpy array of the variable list
    size = len(futo_grid)
    futo_array = np.array(var_list).reshape(-1, size)

    # create a csp object
    model2 = CSP(name='Model 2', vars=var_list)

    # get all_diff constraints for rows
    get_all_different_constraints(model2, futo_array, name='all_diff_row_constraint')

    # get all_diff constraints for columns
    array_transposed = futo_array.transpose()
    get_all_different_constraints(model2, array_transposed, name='all_diff_col_constraint')

    # get the inequality constraints
    get_inequality_constraints(model2, futo_array, futo_grid)

    return model2, futo_array.tolist()   
