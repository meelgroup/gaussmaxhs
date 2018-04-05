#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2018  Mate Soos
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; version 2
# of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

from __future__ import with_statement  # Required in 2.5
from __future__ import print_function
import optparse
from xor_to_cnf_class import *
import sys
import fileinput
import optparse
import random

usage = "usage: %prog [options] --fuzz/--regtest/--checkdir/filetocheck"
desc = """Fuzz the solver with fuzz-generator: ./fuzz_test.py
"""


def set_up_parser():
    parser = optparse.OptionParser(usage=usage, description=desc)
    parser.add_option("--numxors", metavar="NUMXORS", dest="numxors",
                      type=int, default=-1,
                      help="Number of XORs to add. Default: num vars/2")

    parser.add_option("--verbose", "-v", action="store_true", default=False,
                      dest="verbose", help="Print more output")

    return parser


parser = set_up_parser()
(options, args) = parser.parse_args()


def get_max_var(clause):
    maxvar = 0

    tmp = clause.strip()
    if len(tmp) == 0:
        return 0

    assert re.search(r'^x? *-?\d+', tmp)

    if tmp[0] == 'x':
        tmp = tmp[1:]

    for lit in tmp.split():
        var = abs(int(lit))
        maxvar = max(var, maxvar)

    return maxvar


def get_stats(inlines):
    maxvar = 0
    numcls = 0
    extravars_needed = 0
    extracls_needed = 0
    for line in inlines:
        # empty line, skip
        if len(line) == 0:
            continue

        # header or comment
        if line[0] == 'p':
            sp = line.split()
            assert sp[1] == "cnf"
            if maxvar < int(sp[2]):
                maxvar = int(sp[2])
            continue

        if line[0] == 'c':
            continue

        # get max var
        maxvar = max(get_max_var(line), maxvar)
        numcls += 1

    return maxvar, numcls


if __name__ == "__main__":
    # read stdin
    inlines = []
    for line in fileinput.input():
        line = line.strip()
        mysplit = line.split()
        if len(mysplit) == 2:
            assert mysplit[1] == "0"
            # unit clause, skip
            continue

        inlines.append(line)

    numvars, numcls = get_stats(inlines)
    numcls += numvars

    if options.numxors == -1:
        options.numxors = int(numvars/2)

    sys.stdout.write("p wcnf %d %d %d\n" % (numvars,
                                            numcls + numvars + options.numxors,
                                            20))
    atvar = numvars
    for line in inlines:
        # skip empty line
        if len(line) == 0:
            continue

        # skip header and comments
        if line[0] == 'c':
            continue

        if line[0] == 'p':
            continue

        if len(line.split()) == 2:
            # units are not supposed to be here
            assert False
        else:
            # non-unit, add hard weight
            sys.stdout.write("%d %s\n" % (20, line))

    for var in range(1, numvars+1):
        sys.stdout.write("%d %d 0\n" % (1, var))

    for _ in range(options.numxors):
        var_selection = []
        for v in range(1, numvars+1):
            if random.choice([True, False]):
                var_selection.append(v)
        random.shuffle(var_selection)
        var_select_str = [str(x) for x in var_selection]
        sys.stdout.write("x %d %s 0\n" % (20, " ".join(var_select_str)))
