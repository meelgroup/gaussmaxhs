#!/usr/bin/bash

echo "called with seed $1"
./cnf-fuzz-brummayer.py -s $1 | grep -v "^c " > in_cnf
cat in_cnf | ./cnf_to_wcnf_and_xors.py > in_wcnf_xor
cat in_wcnf_xor | ./xor_to_cnf.py > in_wcnf_xor_blasted
echo ./maxhs in_wcnf_xor_blasted

# strip xor for orig maxhs
cat in_wcnf_xor_blasted | ./strip_wcnf.py -x > in_wcnf_xor_blasted_nox
echo ./maxhs_orig in_wcnf_xor_blasted_nox

# hard CNF solving
cat in_wcnf_xor_blasted | ./strip_wcnf.py -s > in_cnf_xors_blasted
echo ~/development/sat_solvers/cryptominisat/build/cryptominisat5 --maxmatrixrows 100000 in_cnf_xors_blasted
cat in_wcnf_xor_blasted | ./strip_wcnf.py -s -x > in_cnf_xor_blasted_nox

echo "diff -y  in_cnf in_wcnf_xor  | colordiff | less -R"
echo "diff -y  in_wcnf_xor in_wcnf_xor_blasted | colordiff | less -R"
echo "diff -y  in_cnf in_cnf_xors_blasted  | colordiff | less -R"
echo "diff -y  in_cnf in_cnf_xor_blasted_nox  | colordiff | less -R"


echo "EXEC! with t-out"
(
ulimit -t 30
echo "-> orig"
echo "./maxhs_orig in_wcnf_xor_blasted_nox > res${1}.orig.out"
./maxhs_orig in_wcnf_xor_blasted_nox > res${1}.orig.out
grep "UNSAT" res${1}.orig.out
grep "^o " res${1}.orig.out
)

(
ulimit -t 30
echo "-> new"
echo "./maxhs in_wcnf_xor_blasted > res${1}.new.out"
./maxhs in_wcnf_xor_blasted > res${1}.new.out
grep "UNSAT" res${1}.new.out
grep "^o " res${1}.new.out
)
