#!/bin/sh
set -e

./GenerateSpinGlass.py --seed $1 --output x

totalorig=0
totalnew=0
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
    /usr/bin/time --verbose -o tmp ./maxhs_orig ${f}_wcnf_xor_blasted_nox > outorig
    grep UNSAT outorig || true
    orig=$(grep "^o " outorig)
    echo $orig
    )
    orig=$(grep "^o " outorig)
    origtime=$(grep "User time" tmp | cut -d " " -f 4)

    (
    ulimit -t 20
    echo "./maxhs ${f}_wcnf_xor_blasted > out"
    /usr/bin/time --verbose -o tmp ./maxhs ${f}_wcnf_xor_blasted > out
    grep UNSAT out || true
    new=$(grep "^o " out)
    echo $new
    )
    new=$(grep "^o " out)
    newtime=$(grep "User time" tmp | cut -d " " -f 4)


    echo "orig vs new time: $origtime --- $newtime"
    totalorig=$(echo "$totalorig + $origtime" | bc)
    totalnew=$(echo "$totalnew + $newtime" | bc)

    if [ "$orig" == "$new" ]; then
        echo "OK: $orig -- $new"
    else
        echo "ERRROR! Not the same result!"
        exit -1
    fi
    echo "Total orig: $totalorig"
    echo "Total new : $totalnew"
done
