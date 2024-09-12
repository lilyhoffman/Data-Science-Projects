import evo
import random as rnd
import numpy as np
import pandas as pd
import random as rnd


# agents, takes in lists, returns one list

NUM_TOGGLES = 3

TAS = pd.read_csv('data/tas.csv')
SECTIONS =pd.read_csv('data/sections.csv')

def _toggle(assignment):
    if assignment == 1:
        return 0
    else:
        return 1
    
def toggle_tas(ta_array_list):
    arr = ta_array_list[0]
    num_rows, num_cols = np.shape(arr)
    for _ in range(1, NUM_TOGGLES):
        point = arr[rnd.randint(0,num_rows - 1)][rnd.randint(0,num_cols - 1)]
        arr[rnd.randint(0,num_rows - 1)][rnd.randint(0,num_cols - 1)] = _toggle(point)
    return arr


# combine two arrays into one
def combine_solutions_agent(ta_arrarys_list):
    first = ta_arrarys_list[0]
    second = ta_arrarys_list[1]
    
    mask = np.random.randint(2, size=first.shape, dtype=bool)
    # np.maximum(first, second)

    return np.where(mask, first, second)


# objectives, lower objective score is better
def over_allocation(sol):
    
    return sum([abs(TAS['max_assigned'][idx] - np.sum(ta)) for idx, ta in enumerate(sol) if TAS['max_assigned'][idx] < np.sum(ta)])


def _any_conflicts(ta):
    
    times = [SECTIONS['daytime'][section] for section in range(0,len(ta)) if ta[section] == 1]
    if len(times) != len(set(times)):
        return 1
    else:
        return 0
    


def time_conflicts(sol):
    return sum([_any_conflicts(ta) for ta in sol])
                
        
def under_support(sol):
    # return sum([sections['min_ta'][idx] - np.sum(section) for idx, section in enumerate(sol.T) if sections['min_ta'][idx] > np.sum(section)])
    return sum((max(0, SECTIONS['min_ta'][idx] - np.sum(section)) for idx, section in enumerate(sol.T)))


def _find_unwilling(idx, ta):
    return sum([1 if ta[section] == 1 and TAS[f'{section}'][idx] == 'U' else 0 for section in range(0,len(ta))])
    

def unwilling(sol):
    return sum([_find_unwilling(idx,ta) for idx, ta in enumerate(sol)])


def _find_unpreferred(idx, ta):
    return sum([1 if ta[section] == 1 and TAS[f'{section}'][idx] == 'W' else 0 for section in range(0,len(ta))])


def unpreferred(sol):
    return sum([_find_unpreferred(idx,ta) for idx, ta in enumerate(sol)])


def main():
    E = evo.Environment()
    
    # register the fitness functions
    E.add_fitness_criteria("over_allocation", over_allocation)
    E.add_fitness_criteria("time_conflicts", time_conflicts)
    E.add_fitness_criteria("under_support", under_support)
    E.add_fitness_criteria("unwilling", unwilling)
    E.add_fitness_criteria("unpreferred", unpreferred)

    # register the agents, not sure on the n here
    E.add_agent("toggle_tas", toggle_tas, k=1)
    E.add_agent("combine_solutions", combine_solutions_agent, k=2)

    # Adding 1 or more initial solution
    i_sol = np.genfromtxt('test_data/test1.csv', delimiter=',', dtype=int)
    E.add_solution(i_sol)

    # Run the evolver
    E.evolve(1000000, 100, 100, runtime=600)



if __name__ == '__main__':
    main()
    
