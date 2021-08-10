#Look for #IMPLEMENT tags in this file. These tags indicate what has
#to be implemented to complete problem solution.  

'''This file will contain different constraint propagators to be used within 
   bt_search.

   propagator == a function with the following template
      propagator(csp, newly_instantiated_variable=None)
           ==> returns (True/False, [(Variable, Value), (Variable, Value) ...]

      csp is a CSP object---the propagator can use this to get access
      to the variables and constraints of the problem. The assigned variables
      can be accessed via methods, the values assigned can also be accessed.

      newly_instaniated_variable is an optional argument.
      if newly_instantiated_variable is not None:
          then newly_instantiated_variable is the most
           recently assigned variable of the search.
      else:
          progator is called before any assignments are made
          in which case it must decide what processing to do
           prior to any variables being assigned. SEE BELOW

       The propagator returns True/False and a list of (Variable, Value) pairs.
       Return is False if a deadend has been detected by the propagator.
       in this case bt_search will backtrack
       return is true if we can continue.

      The list of variable values pairs are all of the values
      the propagator pruned (using the variable's prune_value method). 
      bt_search NEEDS to know this in order to correctly restore these 
      values when it undoes a variable assignment.

      NOTE propagator SHOULD NOT prune a value that has already been 
      pruned! Nor should it prune a value twice

      PROPAGATOR called with newly_instantiated_variable = None
      PROCESSING REQUIRED:
        for plain backtracking (where we only check fully instantiated 
        constraints) 
        we do nothing...return true, []

        for forward checking (where we only check constraints with one
        remaining variable)
        we look for unary constraints of the csp (constraints whose scope 
        contains only one variable) and we forward_check these constraints.

        for gac we establish initial GAC by initializing the GAC queue
        with all constaints of the csp


      PROPAGATOR called with newly_instantiated_variable = a variable V
      PROCESSING REQUIRED:
         for plain backtracking we check all constraints with V (see csp method
         get_cons_with_var) that are fully assigned.

         for forward checking we forward check all constraints with V
         that have one unassigned variable left

         for gac we initialize the GAC queue with all constraints containing V.
		 
		 
var_ordering == a function with the following template
    var_ordering(csp)
        ==> returns Variable 

    csp is a CSP object---the heuristic can use this to get access to the
    variables and constraints of the problem. The assigned variables can be
    accessed via methods, the values assigned can also be accessed.

    var_ordering returns the next Variable to be assigned, as per the definition
    of the heuristic it implements.
   '''
from cspbase import *
from queue import Queue

def prop_BT(csp, newVar=None):
    '''Do plain backtracking propagation. That is, do no 
    propagation at all. Just check fully instantiated constraints'''
    
    if not newVar:
        return True, []
    for c in csp.get_cons_with_var(newVar):
        if c.get_n_unasgn() == 0:
            vals = []
            vars = c.get_scope()
            for var in vars:
                vals.append(var.get_assigned_value())
            if not c.check(vals):
                return False, []
    return True, []

# helper function to build up list for vals in a constraint's scope
def build_scope_vals(constraint, varX):
    '''
    Build up a list of val with Var_X = d to check if all variable assignments
    satisfy or falsify the constraint
    '''
    vals = list()
    varX_idx = -1
    for idx, var in enumerate(constraint.get_scope()):
        if var.get_assigned_value() != None:
            vals.append(var.get_assigned_value())
        elif var == varX:
            vals.append(None)
            varX_idx = idx
    
    return vals, varX_idx

def prop_FC(csp, newVar=None):
    '''Do forward checking. That is check constraints with 
       only one uninstantiated variable. Remember to keep 
       track of all pruned variable,value pairs and return '''

    #initialize variables
    cons = None
    res = list()

    # get the constraints dependings on newVar
    # if newVar has a value, get all the constraints
    if newVar:
        cons = csp.get_cons_with_var(newVar)
    # if newVar == None, get all the constraints
    else:
        cons = csp.get_all_cons()

    # FC over the constraints
    for con in cons:

        # ensure the current constraint has only 1 unassigned variable
        if con.get_n_unasgn() != 1:
            continue

        # var_X is now the unassigned variable in the current constraint
        var_X = con.get_unasgn_vars()[0]    # there is only 1

        vals = list()
        varX_idx = -1

        # get list of scope values with index of varx
        vals, varX_idx = build_scope_vals(con, var_X)

        # do FC for the constraint 
        for val in var_X.cur_domain():

            # assigne value of var_X 
            vals[varX_idx] = val

            # if X = val and con is falsified, remove from current domain
            if not con.check(vals):

                # add to the pruning list for that variable
                var_X.prune_value(val)

                # add var/value pair to pruned list
                res.append((var_X, val))
            
        # if domain of var_X is empty, stop FC
        if var_X.cur_domain_size() == 0:
            return False, res

    return True, res

def prop_GAC(csp, newVar=None):
    '''Do GAC propagation. If newVar is None we do initial GAC enforce 
       processing all constraints. Otherwise we do GAC enforce with
       constraints containing newVar on GAC Queue'''

    cons = None
    res = list()
    queue = Queue()

    # if newVar has something, do GAC for constraints containing newVar
    if newVar:
        for con in csp.get_cons_with_var(newVar):
            queue.put(con)
    else:
        for con in csp.get_all_cons():
            queue.put(con)
    
    while not queue.empty():

        con = queue.get()

        for V in con.get_scope():
            for d in V.cur_domain():

                if not con.has_support(V, d):
                    res.append((V, d))
                    V.prune_value(d)
                
                    if V.cur_domain_size() == 0:
                        return False, res
                    else:
                        for _con in csp.get_cons_with_var(V):
                            if _con not in queue.queue:
                                queue.put(_con)

    return True, res

def ord_mrv(csp):
    ''' return variable according to the Minimum Remaining Values heuristic '''
    # return the variablw with the fewest legal values
    # get all unassigned variables
    vars = csp.get_all_unasgn_vars()

    # find the variable with the smallest current domain size
    domain_sizes = [var.cur_domain_size() for var in vars]   
    min_idx = domain_sizes.index(min(domain_sizes))

    return vars[min_idx]