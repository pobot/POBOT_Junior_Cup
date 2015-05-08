#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Eric Pascual'


from pyevolve.G2DList import G2DList
from pyevolve.GSimpleGA import GSimpleGA


def eval_function(chromosome):
    print("--------- chr=%s" % chromosome.genomeList)
    for planning in chromosome:
        print("planning=%s" % planning)
        matches = planning[:3]
        presentation = planning[-1]
        if sorted(matches) != matches:
            print('** matches in wrong sequence')
            return 0

        for t in zip(matches, matches[1:]):
            if t[1] - t[0] < 3:
                print("** matches too close")
                return 0

        # print("matches=%s" % matches)
        # print("[presentation] * 3=%s" % ([presentation] * 3))
        # print(zip(matches, [presentation] * 3))
        for t in zip(matches, [presentation] * 3):
            if 0 <= t[1] - t[0] < 2:
                print("** presentation too close to match")
                return 0
            if 0 <= t[0] - t[1] <= 4:
                print("** match during presentation")
                return 0

    print('stage 2')
    for slot in range(4):
        t = [chromosome[i][slot] for i in len(chromosome)]
        if len(t) != len(set(t)):
            return 0

    print("Got a working one !!")
    free = sum((t[1] - t[0] for p in chromosome for sp in sorted(p) for t in (sp[0], sp[-1])))
    return free


def main():
    genome = G2DList(7, 4)
    genome.evaluator.set(eval_function)
    genome.setParams(rangemin=0, rangemax=30)
    ga = GSimpleGA(genome)
    ga.setGenerations(100)
    try:
        ga.evolve(freq_stats=0)
    except Exception as e:
        print(e)
    else:
        best = ga.bestIndividual()
        if best.fitness:
            print("Success !!!")
            print(best.genomeList)
        else:
            print("Sorry, no valid planning found :(")

if __name__ == '__main__':
    main()