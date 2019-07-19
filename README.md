# Bender-decomposition---a-toy-model
This is a toy model for bender decomposition. 

Detailed steps have been written in code files as annotations. For the sake of completeness, main ideas are described as follows:

Step 1:
    1.0. establish the master problem
    1.1. add initial constraints
    1.2. solve master problem
    1.3. get solutions(x,\ita) for the subproblem

Step 2:
    for k-th scenarios:
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
                    
Step 3:
    3.1. solve master problem again, and repeat above iterations untill \ita is equal to 
    the objective values of the subproblem
    
 
The most confused part, in my opinion, is part 2 about HOW to verify the optimality of current solution, HOW to identify feasibility constraints, and HOW to find out optimality constraints.
Although starting with a master problem with nice initail constraints is wonderful, the step 2 really made me annoying a lot.

For starters, there are some reading materials, which may help you a lot: (I LOVE THE FIFTH ONE!! It has wonderful pictures explaining details!!!!)
[1] https://orinanobworld.blogspot.com/2012/07/benders-decomposition-in-cplex.html
[2] https://web.stanford.edu/class/msande348/papers/bendersingams
[3] http://cgm.cs.mcgill.ca/~avis/courses/567/notes/stoch3.pdf
[4] http://egon.cheme.cmu.edu/ewo/docs/SPSeminarSchaefer_October16.pdf
[5] http://www.optimization-online.org/DB_FILE/2013/12/4157.pdf

ANY QUESTIONS ARE WELCOMED ~ PLEASE SEND ME EMAIL

