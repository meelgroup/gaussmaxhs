#!/bin/bash

set -e
set -x

numxors=$1
tlimit=$2
memlimit=$3
echo "xors: ${numxors}"
echo "tlimit: ${tlimit}  memlimit ${memlimit}"

totalorig=0
totalnew=0

cp network-reliability/Net22_75_10_count_116.cnf .
f="Net22_75_10_count_116.cnf"
preset="mystuff"
rm -f "${preset}-orig"
mv ${f} "${preset}-orig"
echo "----------------"
echo "Converting $f"
cat "${preset}-orig" | ./xor_to_cnf.py > "${preset}_wcnf_xor_blasted"

# strip xor for orig maxhs
cat "${preset}_wcnf_xor_blasted" | ./strip_wcnf.py -x > "${preset}_wcnf_xor_blasted_nox"

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

rm ${preset}_wcnf*

if [ "$orig" == "$new" ]; then
    echo "OK: $orig -- $new"
else
    echo "ERRROR! Not the same result!"
fi
echo "Total orig: $totalorig"
echo "Total new : $totalnew"
