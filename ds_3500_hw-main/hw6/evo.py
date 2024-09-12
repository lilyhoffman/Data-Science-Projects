"""
File: evo.py
Description: An evolutionary computing framework for multi-objective optimization
"""

import random as rnd
import copy
from functools import reduce
import time
import pandas as pd


class Environment:
    def __init__(self):
        """ Environment constructor """
        self.pop = {}       # evaluation -> solution e.g.,  ((cost, 5), (time, 3), (dist, 10)) --> city sequences
        self.fitness = {}   # objectives / fitness functions:   name->f
        self.agents = {}    # agents:   name -> (operator/function, num_solutions_input)

    def size(self):
        """ The size of the current population """
        return len(self.pop)

    def add_fitness_criteria(self, name, f):
        """ Add or declare an objective to the framework """
        self.fitness[name] = f

    def add_agent(self, name, op, k=1):
        """ Register a named agent with the framework
        The operator (op) function defines what the agent does.
        k defines the number of input solutions that the agent operates on """
        self.agents[name] = (op, k)

    def add_solution(self, sol):
        """ Evaluate and Add a solution to the population """
        eval = tuple([(name, f(sol)) for name, f in self.fitness.items()])
        self.pop[eval] = sol

    def get_random_solutions(self, k=1):
        """ Pick k random solutions from the population
        and return as a list """
        if self.size() == 0:
            return []
        else:
            popvals = tuple(self.pop.values())
            return [copy.deepcopy(rnd.choice(popvals)) for _ in range(k)]

    def run_agent(self, name):
        """ Invoke an agent against the population """
        op, k = self.agents[name]
        picks = self.get_random_solutions(k)
        new_solution = op(picks)
        self.add_solution(new_solution)

    @staticmethod
    def _dominates(p, q):
        """ p, q are the evaluations of the solutions """
        pscores = [score for _,score in p]
        qscores = [score for _,score in q]
        score_diffs = list(map(lambda x,y: y-x, pscores, qscores))
        min_diff = min(score_diffs)
        max_diff = max(score_diffs)
        return min_diff >= 0.0 and max_diff > 0.0

    @staticmethod
    def _reduce_nds(S, p):
        return S - {q for q in S if Environment._dominates(p,q)}

    def remove_dominated(self):
        nds = reduce(Environment._reduce_nds, self.pop.keys(), self.pop.keys())
        self.pop = {k:self.pop[k] for k in nds}

    def evolve(self, n=1, dom=100, status=100, runtime=600):
        start_time = time.time()
        agent_names = list(self.agents.keys())
        for i in range(n):
            pick = rnd.choice(agent_names)
            self.run_agent(pick)
            if i % dom == 0:
                self.remove_dominated()
            if i % status == 0:
                # self.remove_dominated()
                print("Iteration:", i)
                print("Population Size:", self.size())
                print(self)
            et = time.time()
            if et - start_time >= runtime:
                # return a csv report
                print("Out of time!")
                break
                

        # cleaning up the population on last time
        self.remove_dominated()
        self.create_csv_report()

    def __str__(self):
        """ Output the solutions in the population """
        rslt = ""
        for eval,sol in self.pop.items():
            rslt += str(dict(eval))+":\t"+"\n"
        return rslt
    
    def create_csv_report(self):
        rows = [dict({'groupname': 'branlily'}, **dict(eval)) for eval, sol in self.pop.items()]
        df = pd.DataFrame(rows)
        return df.to_csv('ta_evo_report.csv', index=False)
        
            

