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

usage = "usage: cat file | %prog [options] > outfile"
desc = """Strip XORs from file. Can ALSO strip weights if set -s flag.
"""


def set_up_parser():
    parser = optparse.OptionParser(usage=usage, description=desc)
    parser.add_option("--verbose", "-v", action="store_true", default=False,
                      dest="verbose", help="Print more output")
    parser.add_option("--xortoo", "-x", action="store_true", default=False,
                      dest="strip_x", help="Strips XOR clauses from WCNF")
    parser.add_option("--softtoo", "-s", action="store_true", default=False,
                      dest="strip_s", help="Strips soft clauses and makes a normal CNF")

    return parser


parser = set_up_parser()
(options, args) = parser.parse_args()
sys.argv = args


def get_max_var(clause):
    maxvar = 0

    tmp = clause.strip()
    if len(tmp) == 0:
        return 0

    assert re.search(r'^x? *-?\d+', tmp)

    if tmp[0] == 'x':
        tmp = tmp[1:]

    # first value is weight
    for lit in tmp.split()[1:]:
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
            assert sp[1] == "wcnf"
            if maxvar < int(sp[2]):
                maxvar = int(sp[2])
            weight = int(sp[4])
            continue

        if line[0] == 'c':
            continue

        # get max var
        maxvar = max(get_max_var(line), maxvar)
        numcls += 1

    return maxvar, numcls, weight


if __name__ == "__main__":
    # read stdin
    inlines = []
    for line in fileinput.input():
        line = line.strip()
        if line == "":
            continue

        if line[0] == 'x' and options.strip_x:
            # xor clause, skip
            continue

        inlines.append(line)

    numvars, numcls, weight = get_stats(inlines)

    if options.strip_s:
        sys.stdout.write("p cnf %d %d\n" % (numvars, numcls))
    else:
        sys.stdout.write("p wcnf %d %d %d\n" % (numvars, numcls, weight))
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

        if not options.strip_s:
            sys.stdout.write("%s\n" % line)
        else:
            is_xor = False
            line = line.split()
            if line[0] == 'x':
                is_xor = True
                line = line[1:]

            w = int(line[0])
            if w >= weight:
                if is_xor:
                    sys.stdout.write("x ")
                sys.stdout.write("%s\n" % " ".join(line[1:]))

