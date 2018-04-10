#!/bin/sh
set -e

./GenerateSpinGlass.py --seed $1 --output x

for x in {2..15}; do
    f="x_${x}.grid"
    echo "Converting $f"
    cat $f | ./xor_to_cnf.py > ${f}_wcnf_xor_blasted

    # strip xor for orig maxhs
    cat ${f}_wcnf_xor_blasted | ./strip_wcnf.py -x > ${f}_wcnf_xor_blasted_nox

    echo "running $f"
    (
    ulimit -t 20
    echo "./maxhs_orig ${f}_wcnf_xor_blasted_nox > outorig"
    ./maxhs_orig ${f}_wcnf_xor_blasted_nox > outorig
    grep UNSAT outorig || true
    orig=$(grep "^o " outorig)
    echo $orig
    )
    orig=$(grep "^o " outorig)

    (
    ulimit -t 20
    echo "./maxhs ${f}_wcnf_xor_blasted > out"
    ./maxhs ${f}_wcnf_xor_blasted > out
    grep UNSAT out || true
    new=$(grep "^o " out)
    echo $new
    )
    new=$(grep "^o " out)

    if [ "$orig" == "$new" ]; then
        echo "OK: $orig -- $new"
    else
        echo "ERRROR! Not the same result!"
        exit -1
    fi
done
