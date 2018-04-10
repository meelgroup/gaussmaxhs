import sys
import os
import argparse
import random

def GenerateCNF(gridSize,c,roundDigits,outputFile):
    numVars = gridSize*gridSize
    numClauses = 0
    topWeight = 0
    writeStr = ''
    #writeStr = 'p wcnf '+str(numVars)+' '+str(numClauses)+' 1 \n'
    #Adding weights for each vars own state
    for i in range(1, numVars+1):
        weight = int(round(random.uniform(-1,1),roundDigits)*pow(10,roundDigits))
        if (weight > 0):
            topWeight += weight
            writeStr += str(weight)+' '+str(i)+' 0\n'
        else:
            writeStr += str(-weight)+' '+str(-i)+' 0\n'
        numClauses += 1
    #Adding clauses for pairwise interaction of horizontal edges
    for i in range(1,gridSize):
        for j in range(1, gridSize):
            weight = int(round(random.uniform(0,c),roundDigits)*pow(10,roundDigits))
            topWeight += weight
            writeStr += str(weight)+' '+str(i*gridSize+j)+' '+str(i*gridSize+j+1)+ '0 \n'
            numClauses += 1
            writeStr += str(weight)+' '+str(-(i*gridSize+j))+' '+str(-(i*gridSize+j+1))+' 0\n'
            numClauses += 1
    #Adding clauses for pairwise interaction of veritical edges
    for i in range(1, gridSize):
        for j in range(1,gridSize):
            weight = int(round(random.uniform(0,c),roundDigits)*pow(10,roundDigits))
            topWeight += weight 
            writeStr += str(weight)+' '+str(i*gridSize+j)+' '+str(i*gridSize+j+gridSize)+' 0\n'
            numClauses += 1
            writeStr += str(weight)+' '+str(-(i*gridSize+j))+' '+str(-(i*gridSize+j+gridSize))+' 0\n'
            numClauses += 1
    topWeight += 1
    header = 'p wcnf '+str(numVars)+' '+str(numClauses)+' '+str(topWeight)+'\n'
    writeStr = header + writeStr
    f = open(outputFile,'w')
    f.write(writeStr)
    f.close()
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", help="seed for random engine", type=int, default=1)
    parser.add_argument("--output", help="output file prefix",default="log")
    parser.add_argument("--crange", help="range for coupling parameters", type=int, default=3)
    parser.add_argument("--roundDigits", help="number of digits weight function should be rounded", type=int,default=3)
    parser.add_argument("--gridSize", help="Grid Size", type=int, default=7)
    args = parser.parse_args()
    seed = args.seed
    outputFile = args.output
    crange = args.crange
    gridSize = args.gridSize
    roundDigits = args.roundDigits
    index = 1
    for i in range(2,crange*10,2):
        index += 1
        c = i*1.0/10
        GenerateCNF(gridSize,c,roundDigits, outputFile+"_"+str(index)+".grid")
        


main()
