[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# GaussMaxHS, a CNF-XOR MaxSAT solver based on MaxHS

The code uses [MiniSat](https://github.com/niklasso/minisat) as the SAT solver, [CPLEX](https://community.ibm.com/community/user/datascience/blogs/xavier-nodet1/2020/07/09/cplex-free-for-students?mhsrc=ibmsearch_a&mhq=cplex) from IBM as the MIPS solver, [MaxHS](https://github.com/fbacchus/MaxHS) for MaxSAT solving, and a version of Gauss-Jordan elimination to perform CDCL(T). For our research paper PDF, see [here](https://proceedings.kr.org/2021/55/kr2021-0055-soos-et-al.pdf), published at Knowledge Representation and Reasoning (KR) 2021 ([Bibtex](https://proceedings.kr.org/2021/55/bibtex/))


## Building and installing
### Get CPLEX

You need the CPLEX static libraries to link against. CPLEX is
available from IBM under their academic Initiative program. It is
free to faculty members and graduate students in academia, see [here](https://community.ibm.com/community/user/datascience/blogs/xavier-nodet1/2020/07/09/cplex-free-for-students?mhsrc=ibmsearch_a&mhq=cplex).

You can apply for their academic initiative program and then then you
can download CPLEX and other IBM software.

### Configure and Build
Use `make config VAR=defn` or edit `config.mk` directly. Required variable settings:

- Linux: `LINUX_CPLEXLIBDIR=<path to CPLEX library>` the directory on your linux system that contains libcplex.a and libilocplex.a (the makefile does a static build). `LINUX_CPLEXINCDIR=<path to CPLEX headers>`
- MacOS: `DARWIN_CPLEXLIBDIR=<path to CPLEX library>` the directory on your MAC system that contains libcplex.a and libilocplex.a (the makefile does a static build), `DARWIN_CPLEXINCDIR=<path to CPLEX headers>`


After the above configuration, you can:
```
make install
```

## How to Run

The system expects a CNF-XOR input, which is the same as the [WDIMACS](http://www.maxhs.org/docs/wdimacs.html) format with the extension that you can add XOR constraints just like with [CryptoMiniSat](https://github.com/msoos/cryptominisat), and the weight must be provided after the 'x'. For example, let's take the following input file:

```
p wcnf 4 3 10
10 1 -2 3 0
x 5 1 2 0
x 5 -1 3 4 0
```

This file contains four variables and thee constraints, and promises to give weights with a hard constraint having a weight of 10 (hence the header `p wcnf 4 3 10`). The first constraint says that `v1 or not v2 or v3 = true` and has a weight of 10, i.e. it's a hard constraints. The second says that `v1 XOR x2 = true` and the third says `v1 XOR v3 XOR v4 = false`, both of which have a weight of 5, and are soft constraints.


## Generating Spin Glass and Network Reliability problems
You will find `generate-netrel.sh` and `generate-spin.sh` problem generators under the default binary location `build/release/bin`. You can run these scripts to generate example [Spin Glass](https://cs.stanford.edu/~ermon/papers/rademacher-aaai2018.pdf) and [Network Reliability problems](https://www.comp.nus.edu.sg/~meel/Papers/AAAI17.pdf) for you.

To run the `generate-netrel.sh` script, you will need to extract the files from `build/release/bin/network-reliability/net-rel.tar.gz` first. The files should all be extracted under `build/release/bin/network-reliability/`, e.g. one file should be `build/release/bin/network-reliability/Net27_90_22_count_118.cnf`.


## Fuzzing
You can find various fuzzers for the GaussMaxHS system under `build/release/bin`, the default binary location. You can run `fuzz.sh` to fuzz the system against MaxHS without Gauss-Jordan elimination. While this fuzzing is incomplete, it should find most bugs. You will need [CryptoMiniSat5](https;//www.github.com/msoos/cryptominisat) installed, as the script uses CryptoMiniSat to check for errors with GJE.
