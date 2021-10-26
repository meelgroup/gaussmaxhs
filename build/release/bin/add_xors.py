#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2019 Mate Soos

import argparse
import random
import re

def read_file():
    dat=[]
    with open(args.f) as f:
        for line in f:
            dat.append(line.strip())
            #print(line.strip())

    return dat

def get_max_var(clause):
        maxvar = 0

        tmp = clause.strip()
        if len(tmp) == 0:
            return 0

        assert re.search(r'^x? *-?\d+', tmp)

        if tmp[0] == 'x':
            tmp = tmp[1:]

        if True:
            tmp = " ".join(tmp.split()[1:])

        for lit in tmp.split():
            var = abs(int(lit))
            maxvar = max(var, maxvar)

        return maxvar

def get_stats(dat):
        maxvar = 0
        numcls = 0
        for line in dat:
            line = line.strip()

            # empty line, skip
            if len(line) == 0:
                continue

            # header or comment
            if line[0] == 'p':
                if "wcnf" in line:
                    wcnf = int(line.split()[4])
                continue

            if line[0] == 'c':
                continue

            # get max var
            maxvar = max(get_max_var(line), maxvar)
            numcls += 1

        return [maxvar, numcls, wcnf]

def add_xors(dat):
    numVars, numcls, topWeight = get_stats(dat)

    writeStr =""
    for d in dat:
        if "p wcnf" not in d:
            writeStr += d + "\n"

    # Adding XORs
    for _ in range(args.xors):
        writeStr += "x %d " % (topWeight)
        for i in range(1, numVars + 1):
            if random.choice([True, False]):
                writeStr += "%d " % i
        writeStr += "0\n"
        numcls += 1

    header = 'p wcnf ' + str(numVars) + ' ' + \
        str(numcls) + ' ' + str(topWeight) + '\n'
    writeStr = header + writeStr

    f = open(args.o, 'w')
    f.write(writeStr)
    f.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--xors", help="num xors to add",
                        type=int)
    parser.add_argument("-f", help="File input", type=str)
    parser.add_argument("-o", help="File output", type=str)
    parser.add_argument("--seed", help="seed for random engine", type=int,
                        default=1)

    args = parser.parse_args()
    random.seed(args.seed)
    print("seed:", args.seed)

    if args.f is None:
        print("ERROR: must give file name")
        exit(-1)

    if args.xors is None:
        print("ERROR: must give XOR count")
        exit(-1)

    if args.o is None:
        print("ERROR: must give output file")
        exit(-1)

    dat = read_file()
    add_xors(dat)
