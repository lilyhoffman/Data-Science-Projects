import pytest
import numpy as np
from ta_evo import over_allocation, under_support, unwilling, unpreferred, time_conflicts

@pytest.fixture
def solutions():
    test1 = np.genfromtxt('test_data/test1.csv', delimiter=',', dtype=int)
    test2 = np.genfromtxt('test_data/test2.csv', delimiter=',', dtype=int)
    test3 = np.genfromtxt('test_data/test3.csv', delimiter=',', dtype=int)
    return [test1,test2,test3]

def test_overallocation(solutions):
    expected = [37,41,23]
    
    for idx,test in enumerate(solutions):
        e = expected[idx]
        actual = over_allocation(test)
        assert e == actual
    

def test_undersupport(solutions):
    expected = [1,0,7]
    
    for idx,test in enumerate(solutions):
        e = expected[idx]
        actual = under_support(test)
        assert e == actual  
    
def test_unwilling(solutions):
    expected = [53,58,43]
    
    for idx,test in enumerate(solutions):
        e = expected[idx]
        actual = unwilling(test)
        assert e == actual   

def test_unpreferred(solutions):
    expected = [15,19,10]
    
    for idx,test in enumerate(solutions):
        e = expected[idx]
        actual = unpreferred(test)
        assert e == actual   

def test_timeconflict(solutions):
    expected = [8,5,2]
    
    for idx,test in enumerate(solutions):
        e = expected[idx]
        actual = time_conflicts(test)
        assert e == actual 
    
    
    


    