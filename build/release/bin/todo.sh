#!/usr/bin/sh

ulimit -t 30
set -e
./xor_to_cnf.py a.cnf b.cnf
cat b.cnf
echo "///"
echo "num clauses:"
grep -v "^c" b.cnf | grep -v "^p" | wc -l

