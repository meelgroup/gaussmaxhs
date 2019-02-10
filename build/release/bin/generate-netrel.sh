#!/bin/bash

set -x

function compare_the_two
{
    echo "running $f"
    (
        rm -f "${preset}.outorig"
        ulimit -t "$tlimit"
        ulimit -v "$memlimit"
        /usr/bin/time --verbose -o "${preset}.timeoutorig" ./maxhs_orig -verb=0 "${preset}_wcnf_xor_blasted_nox" > "${preset}.outorig"
        grep UNSAT "${preset}.outorig" || true
        orig=$(grep "^o " "${preset}.outorig")
        echo "$orig"
    )
    orig=$(grep "^o " "${preset}.outorig")
    origtime=$(grep "User time" "${preset}.timeoutorig" | cut -d " " -f 4)

    (
        rm -f "${preset}.outnew"
        ulimit -t "$tlimit"
        ulimit -v "$memlimit"
        /usr/bin/time --verbose -o "${preset}.timeoutnew" ./maxhs -verb=0  "${preset}_wcnf_xor_blasted" > "${preset}.outnew"
        grep UNSAT "${preset}.outnew" || true
        new=$(grep "^o " "${preset}.outnew")
        echo "$new"
    )
    new=$(grep "^o " "${preset}.outnew")
    newtime=$(grep "User time" "${preset}.timeoutnew" | cut -d " " -f 4)


    echo "orig vs new time: $origtime --- $newtime"
    totalorig=$(echo "$totalorig + $origtime" | bc)
    totalnew=$(echo "$totalnew + $newtime" | bc)
}

tlimit=$1
memlimit=$2

if [[ $tlimit == "" ]]; then
	echo "ERROR You must give timeout as 2nd argument"
	exit -1
fi

if [[ $memlimit == "" ]]; then
	echo "ERROR You must give mem limit in kb as 3rd argument"
	exit -1
fi
echo "tlimit: ${tlimit}  memlimit ${memlimit}"


totalorig=0
totalnew=0
ls network-reliability/*.cnf > mylist
shuf mylist | head -n 1 > mylist2

for f in `cat mylist2` ;do
    for numxors in {0..2} ;do
        f=$(basename "$f")
        cp "network-reliability/$f" .
        ./add_xors.py -f "$f" -o "$f-withxors" --xors $numxors

        f="$f-withxors"
        preset="$f"
        rm -f "${preset}-orig"
        mv ${f} "${preset}-orig"
        echo "----------------"
        echo "Converting $f"
        cat "${preset}-orig" | ./xor_to_cnf.py > "${preset}_wcnf_xor_blasted"

        # strip xor for orig maxhs
        cat "${preset}_wcnf_xor_blasted" | ./strip_wcnf.py -x > "${preset}_wcnf_xor_blasted_nox"

        compare_the_two

        rm "${preset}.outnew"
        rm "${preset}.outorig"
        rm "${preset}.timeoutorig"
        rm "${preset}.timeoutnew"

        if [ "$orig" == "$new" ]; then
            echo "OK: $orig -- $new"
        else
            echo "ERRROR! Not the same result!"
        fi
    done
done

echo "Total orig: $totalorig"
echo "Total new : $totalnew"
