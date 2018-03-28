#ifndef GAUSS_CONFIG_H
#define GAUSS_CONFIG_H

namespace Minisat {
class GaussConf
{
    public:

    GaussConf() :
        only_nth_gauss_save(2)
        , decision_until(700)
        , autodisable(true)
        , iterativeReduce(true)
        , max_matrix_rows(800)
        , min_matrix_rows(15)
        , max_num_matrixes(2)
    {
    }

    uint32_t only_nth_gauss_save;  //save only every n-th gauss matrix
    uint32_t decision_until; //do Gauss until this level
    bool autodisable; //If activated, gauss elimination is never disabled
    bool iterativeReduce; //Minimise matrix work
    uint32_t max_matrix_rows; //The maximum matrix size -- no. of rows
    uint32_t min_matrix_rows; //The minimum matrix size -- no. of rows
    uint32_t max_num_matrixes; //Maximum number of matrixes

    //Matrix extraction config
    bool doMatrixFind = true;
    uint32_t min_gauss_xor_clauses = 3;
    uint32_t max_gauss_xor_clauses = 500000;
};

}

#endif //GAUSS_CONFIG_H
