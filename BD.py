# -*- coding: utf-8 -*-
"""
Created on Fri Apr 26 22:17:04 2019

@author: chend
"""

from gurobipy import gurobipy as grb
import numpy as np
import itertools

def AddInitialConstraints(masterProblem):
    '''
    TODO:
        automatically find out initial constraints
    '''
    pass

    return masterProblem

def addFeasibilityCut(masterProblem,subProblem,A,b,n):
    # find the extreme ray
    # !!! FarkasDual gets the reverse-directional extreme ray
    extremeRay = -np.asarray(subProblem.FarkasDual)
    
    #add feasiblity cut: r^j(b-Ax) <= 0
    feasibilitycut = grb.quicksum(extremeRay[i]*(b[n][i] - grb.quicksum(A[i][j]*X[j+1] for j in range(A.shape[1])))
                            for i in range(A.shape[0])) <= 0
    masterProblem.addConstr(feasibilitycut)
    #print('add FFF:', feasibilitycut)
    
def addOptimalityCut(masterProblem,subProblem,A,b,n):
    # get dual value
    dualValue = subProblem.Pi
    
    #add optimality cut \ita
    optimalitycut = ITA[n+1]-grb.quicksum(dualValue[i]*(b[n][i] - grb.quicksum(A[i][j]*X[j+1] for j in range(A.shape[1]))) 
                            for i in range(A.shape[0]))>=0
    masterProblem.addConstr(optimalitycut)
    #print('add FFF:', optimalitycut)

if __name__ == '__main__':
    
    # scenarios-related information
    SCENARIOS = [[i,j] for i,j in itertools.product(np.random.normal(loc=5,scale=0.5,size=100),np.random.normal(loc=100,scale=15,size=200))]
    k = len(SCENARIOS)
    
    # iteration parameters
    TOLERANCE = 0.0001
    MAX_ITERATION = 500

    # C^t X:
    C = [3,2]
    
    #h^t Y:
    H = [15,12]
    
    #GY <= b-AX
    G = np.asarray([
     [-3,-2],
     [-2,-5],
     [-1,0],
     [1,0],
     [0,-1],
     [0,1]])
    
    A = np.asarray([
     [1,0],
     [0,1],
     [0,0],
     [0,0],
     [0,0],
     [0,0]])
    
    b = np.asarray(
    [[0,
     0,
     -SCENARIOS[n][0],
     SCENARIOS[n][0]*0.8,
     -SCENARIOS[n][1],
     SCENARIOS[n][1]*0.8] for n in range(k)])
    
    '''
    Step 1:
        1.0. establish the master problem
        1.1. add initial constraints
        1.2. solve master problem
        1.3. get solutions(x,\ita) for the subproblem
    '''
    # --- 1.0. establish master Model with scenarios
    
    #Build Model
    masterProblem = grb.Model('MasterProblem')
    masterProblem.modelSense = grb.GRB.MINIMIZE
    masterProblem.setParam('OutputFlag',0)
    
    #Create Variables
    #First-stage Variables
    X = masterProblem.addVars([1,2],vtype = grb.GRB.CONTINUOUS,lb=[0,0],obj = [3,2], name='X')
    
    #Second-stage recourse value variables
    ITA = masterProblem.addVars(range(1,k+1),vtype = grb.GRB.CONTINUOUS,lb=-1000000,ub=1000000,obj = [1/k]*k, name='ITA') #arbitrarily give two boundaries that can not be reached    
    
    #Add constraints for the first-stage
    pass

    # --- 1.1. add initial constraints
    masterProblem = AddInitialConstraints(masterProblem)
    
    # --- 1.2. solve master problem
    OPTIMALITY = [False]*k

    while all(OPTIMALITY) == False:
        
        masterProblem.optimize()
        
        # --- 1.3. get solutions(x,\ita) for the subproblem
        x = {i:X[i].x for i in X.keys()}
        ita = {i:ITA[i].x for i in ITA.keys()} #For each scenarios, there is an ita, so it's a list
        print(x)
        print('OPTIMAL SCENARIO NUM:',sum(OPTIMALITY))
        '''    
        Step 2:
            for each scenarios:
            
                2.0. establish the k-th subproblem
                2.1. solve the subproblem to verify whether the current solution (x,\ita^k) is optimal
                    if yes:
                        done
                    else:
                        2.1.1: if subproblem is infeasible:
                            add feasibility constraints to master problem
                        2.1.2: if the objective value of the subproblem is greater(for maxmizing problem) 
                        or smaller(for minimizing problem) than \ita:
                            add optimality constraints to master problem
        '''    
        ADDFEASIBILITYCUT_NUM = 0
        ADDOPTIMALITYCUT_NUM = 0
        
        for n in range(k):
            # --- 2.0. establish the k-th subproblem
            subProblem = grb.Model('subProblem')
            subProblem.modelSense = grb.GRB.MINIMIZE
            subProblem.setParam('OutputFlag',0)
            subProblem.setParam('InfUnbdInfo',1) #InfUnbdInfo is the prerequire for getting FarkasProof attribute
            
            # variables
            Y = subProblem.addVars([1,2],vtype = grb.GRB.CONTINUOUS,lb=[0,0],obj = [15,12], name='Y')
            
            # add second-stage recourse constraints    
            
            subProblem.addConstrs(grb.quicksum(G[i][j]*Y[j+1] for j in range(G.shape[1])) >= b[n][i] - grb.quicksum(A[i][j]*X[j+1].x for j in range(A.shape[1]))
                                    for i in range(G.shape[0]))
            
            # --- 2.1. solve the k-th subproblem
            subProblem.optimize()
            
            # --- 2.1.1. subproblem is infeasible, then add a feasibility cut (should find out the extreme rays)
            if subProblem.Status == grb.GRB.INFEASIBLE:
                addFeasibilityCut(masterProblem,subProblem,A,b,n)
                ADDFEASIBILITYCUT_NUM += 1
                
            # --- 2.1.2. add optimality cut or get optimal solution
            elif subProblem.Status == grb.GRB.OPTIMAL:
                
                # if subproblem == ita, we now get optimal solution in the master problem
                if ita[n+1] >= subProblem.ObjVal - TOLERANCE:
                    OPTIMALITY[n] = True
                    
                # if subproblem objective value > ita, then add an optimality cut
                if ita[n+1] < subProblem.ObjVal :
                    addOptimalityCut(masterProblem,subProblem,A,b,n)
                    ADDOPTIMALITYCUT_NUM += 1
            else:
                print('subProblem Status is Wrong!!!Status Code is:',subProblem.Status)
       
        print('Add %d Feasibility Cuts' %ADDFEASIBILITYCUT_NUM)
        print('Add %d optimality Cuts' %ADDOPTIMALITYCUT_NUM)
        #after add constraint generated by each scenarios, update the master model
        masterProblem.update()
        
    '''
    Step 3:
        3.1. solve master problem again, and repeat above iterations untill \ita is equal to 
        the objective values of the subproblem
    '''
    # --- 3.1. solve master problem again to finally get the optimal solution
    print('Optimal Value reached')
    masterProblem.optimize()
    x = {i:X[i].x for i in X.keys()}
    ita = {i:ITA[i].x for i in ITA.keys()}
    

    
    
    
    
    
    
