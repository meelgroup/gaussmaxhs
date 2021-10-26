# GaussMaxHS, an XOR supporting MaxSAT solver based on MaxHS

The code uses [MiniSat](https://github.com/niklasso/minisat) as the SAT solver, [CPLEX](https://community.ibm.com/community/user/datascience/blogs/xavier-nodet1/2020/07/09/cplex-free-for-students?mhsrc=ibmsearch_a&mhq=cplex) from IBM as the MIPS solver, [MaxHS](https://github.com/fbacchus/MaxHS) for MaxSAT solving, and a version of Gauss-Jordan elimination to perform CDCL(T). For our paper PDF, see [here](https://proceedings.kr.org/2021/55/kr2021-0055-soos-et-al.pdf).


## Building and installing
### Get CPLEX.

You need the CPLEX static libraries to link against. CPLEX is
available from IBM under their academic Initiative program. It is
free to faculty members and graduate students in academia, see [here](https://community.ibm.com/community/user/datascience/blogs/xavier-nodet1/2020/07/09/cplex-free-for-students?mhsrc=ibmsearch_a&mhq=cplex).

You apply for their academic initiative program and then then you
can download CPLEX and other IBM software.

### Configure
Use `make config VAR=defn` or edit config.mk directly. Required variable settings:

- Linux: `LINUX_CPLEXLIBDIR=<path to CPLEX library>` the directory on your linux system that contains libcplex.a and libilocplex.a (the makefile does a static build). `LINUX_CPLEXINCDIR=<path to CPLEX headers>`
- MacOS: `DARWIN_CPLEXLIBDIR=<path to CPLEX library>` the directory on your MAC system that contains libcplex.a and libilocplex.a (the makefile does a static build), `DARWIN_CPLEXINCDIR=<path to CPLEX headers>`

  
### Build
make install

## Generating Spin Glass and Network Reliability problems
You will find `generate-netrel.sh` and `generate-spin.sh` problem generators under the default binary location `build/release/bin`. You can run these scripts to generate example [Spin Glass](https://cs.stanford.edu/~ermon/papers/rademacher-aaai2018.pdf) and [Network Reliability problems](https://www.comp.nus.edu.sg/~meel/Papers/AAAI17.pdf) for you.


## Fuzzing
You can find various fuzzers for the GaussMaxHS system under `build/release/bin`, the default binary location. You can run `fuzz.sh` to fuzz the system against MaxHS without Gauss-Jordan elimination. While this fuzzing is incomplete, it should find most bugs.
