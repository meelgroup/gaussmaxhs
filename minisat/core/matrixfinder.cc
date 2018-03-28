/******************************************
Copyright (c) 2016, Mate Soos

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
***********************************************/

#include "matrixfinder.h"
#include "Solver.h"
#include "gaussian.h"

#include <set>
#include <map>
#include <iomanip>
#include <cmath>
#include "minisat/utils/System.h"

//#define VERBOSE_DEBUG
//#define PART_FINDING

using namespace Minisat;

using std::set;
using std::map;
using std::endl;
using std::cout;

MatrixFinder::MatrixFinder(Solver* _solver) :
    solver(_solver)
{
}

inline uint32_t MatrixFinder::fingerprint(const Xor& x) const
{
    uint32_t fingerprint = 0;

    for (uint32_t v: x)
        fingerprint |= v;

    return fingerprint;
}

inline bool MatrixFinder::firstPartOfSecond(const Xor& c1, const Xor& c2) const
{
    uint32_t i1, i2;
    for (i1 = 0, i2 = 0; i1 < c1.size() && i2 < c2.size();) {
        if (c1[i1] != c2[i2])
            i2++;
        else {
            i1++;
            i2++;
        }
    }

    return (i1 == c1.size());
}

inline bool MatrixFinder::belong_same_matrix(const Xor& x)
{
    uint32_t comp_num = std::numeric_limits<uint32_t>::max();
    for (uint32_t v : x) {
        if (table[v] == var_Undef) {
            //Belongs to none, abort
            return false;
        }

        if (comp_num == std::numeric_limits<uint32_t>::max()) {
            //Belongs to this one
            comp_num = table[v];
        } else {
            if (comp_num != table[v]) {
                //Another var in this XOR belongs to another component
                return false;
            }
        }
    }
    return true;
}

bool MatrixFinder::findMatrixes()
{
    assert(solver->decisionLevel() == 0);
    assert(solver->ok);

    table.clear();
    table.resize(solver->nVars(), var_Undef);
    reverseTable.clear();
    matrix_no = 0;
    double myTime = cpuTime();

    if (solver->xorclauses.size() < solver->gaussconf.min_gauss_xor_clauses
        || solver->gaussconf.decision_until <= 0
    ) {
        return true;
    }

    bool ret = solver->clean_xor_clauses(solver->xorclauses);
    if (!ret)
        return false;

    if (!solver->gaussconf.doMatrixFind) {
        if (solver->verbosity >=1) {
            cout << "c Matrix finding disabled through switch. Putting all xors into matrix." << endl;
        }
        solver->gauss_matrixes.push_back(new Gaussian(solver, solver->xorclauses, 0));
        return true;
    }

    vector<uint32_t> newSet;
    set<uint32_t> tomerge;
    for (const Xor& x : solver->xorclauses) {
        if (belong_same_matrix(x)) {
            continue;
        }

        tomerge.clear();
        newSet.clear();
        for (uint32_t v : x) {
            if (table[v] != var_Undef)
                tomerge.insert(table[v]);
            else
                newSet.push_back(v);
        }
        if (tomerge.size() == 1) {
            const uint32_t into = *tomerge.begin();
            auto intoReverse = reverseTable.find(into);
            for (uint32_t i = 0; i < newSet.size(); i++) {
                intoReverse->second.push_back(newSet[i]);
                table[newSet[i]] = into;
            }
            continue;
        }

        for (uint32_t v: tomerge) {
            newSet.insert(newSet.end(), reverseTable[v].begin(), reverseTable[v].end());
            reverseTable.erase(v);
        }
        for (uint32_t i = 0; i < newSet.size(); i++)
            table[newSet[i]] = matrix_no;
        reverseTable[matrix_no] = newSet;
        matrix_no++;
    }

    #ifdef VERBOSE_DEBUG
    for (map<uint32_t, vector<uint32_t> >::iterator it = reverseTable.begin()
        , end = reverseTable.end()
        ; it != end
        ; ++it
    ) {
        cout << "-- set: " << endl;
        for (vector<uint32_t>::iterator it2 = it->second.begin(), end2 = it->second.end()
            ; it2 != end2
            ; it2++
        ) {
            cout << *it2 << ", ";
        }
        cout << "-------" << endl;
    }
    #endif

    uint32_t numMatrixes = setMatrixes();

    const bool time_out =  false;
    const double time_used = cpuTime() - myTime;
    if (solver->verbosity) {
        cout << "c Found matrixes: " << numMatrixes
        << solver->print_times(time_used, time_out)
        << endl;
    }

    for (Gaussian* g: solver->gauss_matrixes) {
        if (!g->init_until_fixedpoint()) {
            break;
        }
    }

    return solver->ok;
}

uint32_t MatrixFinder::setMatrixes()
{
    if (solver->independent_vars) {
        uint32_t size_at_least = (double)solver->independent_vars->size()*3;
        if (solver->gaussconf.max_matrix_rows < size_at_least) {
            solver->gaussconf.max_matrix_rows = size_at_least;
            if (solver->verbosity) {
                cout << "c [matrixfind] incrementing max number of rows to "
                << size_at_least
                << endl;
            }
        }
    }

    vector<MatrixShape> matrix_shape;
    vector<vector<Xor> > xorsInMatrix(matrix_no);

    for (uint32_t i = 0; i < matrix_no; i++) {
        matrix_shape.push_back(MatrixShape(i));
        matrix_shape[i].num = i;
        matrix_shape[i].cols = reverseTable[i].size();
    }

    for (const Xor& x : solver->xorclauses) {
        //take 1st variable to check which matrix it's in.
        const uint32_t matrix = table[x[0]];
        assert(matrix < matrix_no);

        //for stats
        matrix_shape[matrix].rows ++;
        matrix_shape[matrix].sum_xor_sizes += x.size();
        xorsInMatrix[matrix].push_back(x);
    }

    for(auto& m: matrix_shape) {
        if (m.tot_size() > 0) {
            m.density = (double)m.sum_xor_sizes / (double)(m.tot_size());
        }
    }

    std::sort(matrix_shape.begin(), matrix_shape.end(), mysorter());

    uint32_t realMatrixNum = 0;
    for (int a = matrix_no-1; a >= 0; a--) {
        MatrixShape& m = matrix_shape[a];
        uint32_t i = m.num;
        if (m.rows == 0) {
            continue;
        }

        //cout << "small check" << endl;
        if (m.rows < solver->gaussconf.min_matrix_rows
            || m.rows > solver->gaussconf.max_matrix_rows
        ) {
            if (m.rows > solver->gaussconf.max_matrix_rows
                && solver->verbosity
            ) {
                cout << "c [matrix] Too many rows in matrix: " << m.rows << endl;
            }
            continue;
        }

        double ratio_indep = 0;
        if (solver->independent_vars) {
            uint32_t indep_var_inside_matrix = 0;

            //'seen' with what is in Matrix
            for(uint32_t int_var: reverseTable[i]) {
                solver->seen[int_var] = true;
            }

            for(uint32_t outside_var: *solver->independent_vars) {
                uint32_t outer_var = solver->map_to_with_bva(outside_var);
                outer_var = solver->varReplacer->get_var_replaced_with_outer(outer_var);
                uint32_t int_var = solver->map_outer_to_inter(outer_var);
                if (int_var < solver->nVars()
                    && solver->seen[int_var]
                ) {
                    indep_var_inside_matrix++;
                }
            }

            //Clear 'seen'
            for(uint32_t int_var: reverseTable[i]) {
                solver->seen[int_var] = false;
            }

            ratio_indep = (double)indep_var_inside_matrix/(double)reverseTable[i].size();
        }


        bool use_matrix = false;
        /*if (solver->independent_vars) {
            if (ratio_indep > 1.0) { //TODO Magic constant
                use_matrix = true;
            }
        }*/

        if (realMatrixNum <= solver->gaussconf.max_num_matrixes) {
            use_matrix = true;
        }

        if (use_matrix) {
            if (solver->verbosity) {
                cout << "c [matrix] Good   matrix " << std::setw(2) << realMatrixNum;
            }
            solver->gauss_matrixes.push_back(
                new Gaussian(solver, xorsInMatrix[i], realMatrixNum)
            );
            realMatrixNum++;
        } else {
            if (solver->verbosity) {
                cout << "c [matrix] UNused matrix   ";
            }
        }

        if (solver->verbosity) {
            double avg = (double)m.sum_xor_sizes/(double)m.rows;

            cout << std::setw(7) << m.rows << " x"
            << std::setw(5) << reverseTable[i].size()
            << "  density:"
            << std::setw(5) << std::fixed << std::setprecision(1) << m.density << "%"
            << "  xorlen avg: "
            << std::setw(5) << std::fixed << std::setprecision(2)  << avg
            << "  perc indep: "
            << std::setw(5) << std::fixed << std::setprecision(3) << ratio_indep*100.0 << " %"
            << endl;
        }

#if 0
        vector<uint32_t> vars;
        for(const Xor& x: xorsInMatrix[i]) {
            for(uint32_t var: x) {
                if (!solver->seen[var]) {
                    vars.push_back(var);
                }
                solver->seen[var]++;
            }
        }

        for(const uint32_t var: vars) {
            cout << "c [matrix] num xors touching var " << var << " : " << solver->seen[var] << endl;
            solver->seen[var] = false;
        }

        for(uint32_t outside_var: *solver->independent_vars) {
            uint32_t outer_var = solver->map_to_with_bva(outside_var);
            uint32_t int_var = solver->map_outer_to_inter(outer_var);
            if (int_var < solver->nVars()) {
                solver->seen[int_var] = true;
            }
        }

        for(const Xor& x: xorsInMatrix[i]) {
            bool num_indeps = 0;
            for(uint32_t var: x) {
                vars.push_back(var);
                if (solver->seen[var]) {
                    num_indeps++;
                }
            }
            cout << "c [matrix] num indep perc: " << ((double)num_indeps/(double)x.size())*100.0 << " %" << endl;
        }

        for(uint32_t outside_var: *solver->independent_vars) {
            uint32_t outer_var = solver->map_to_with_bva(outside_var);
            uint32_t int_var = solver->map_outer_to_inter(outer_var);
            if (int_var < solver->nVars()) {
                solver->seen[int_var] = false;
            }
        }
#endif

    }

    return realMatrixNum;
}

