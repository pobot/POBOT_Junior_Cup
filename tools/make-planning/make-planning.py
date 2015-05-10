#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Eric Pascual'


from pyevolve.G2DList import G2DList
from pyevolve.GSimpleGA import GSimpleGA, ConvergenceCriteria
from pyevolve import Crossovers
from pyevolve import Mutators

import random

MATCH_COUNT = 3
JURY_POS = MATCH_COUNT

MAX_SLOTS = 30
MATCH_SLOTS = range(MAX_SLOTS)
MATCH_SLOTS_SET = set(MATCH_SLOTS)

JURY_SLOTS = range(0, MAX_SLOTS, 3)
JURY_SLOTS_SET = set(JURY_SLOTS)

MATCH_NUMS = range(MATCH_COUNT)

TEAM_COUNT = 7
TEAM_NUMS = range(TEAM_COUNT)


def eval_function(chromosome):
    # print("--------- chr=%s" % chromosome.genomeList)
    max_score = 0
    fitness = 0.0

    for planning in chromosome:
        # print("planning=%s" % planning)
        matches = planning[:MATCH_COUNT]
        presentation = planning[JURY_POS]

        max_score += 1
        if sorted(matches) == matches:
            # print('** matches sequence OK')
            fitness += 1

        max_score += 1
        if all([3 < dt < 6 for dt in (matches[1] - matches[0], matches[2] - matches[1])]):
            # print("** matches distance OK")
            fitness += 1

        # print("matches=%s" % matches)
        # print("[presentation] * 3=%s" % ([presentation] * 3))
        # print(zip(matches, [presentation] * 3))
        for match, pres in zip(matches, [presentation] * MATCH_COUNT):
            max_score += 1
            if pres - match >= 2:
                # print("** match-presentation distance OK")
                fitness += 1
            elif match - pres >= 4:
                # print("** presentation-match distance OK")
                fitness += 1

    solution = chromosome.genomeList
    for match in MATCH_NUMS:
        max_score += 1
        t = [solution[i][match] for i in TEAM_NUMS]
        if len(t) == len(set(t)):
            # print('** no table contention')
            fitness += 1
        else:
            return 0

    t = solution[:][JURY_POS]
    max_score += 1
    if len(t) == TEAM_COUNT:
        d = min(
            abs(t[1] - t[0]), abs(t[2] - t[0]), abs(t[3] - t[0]),
            abs(t[2] - t[1]), abs(t[3] - t[1]),
            abs(t[3] - t[2])
        )
        if d > 3:
            # print('** no jury contention')
            fitness += 1
        else:
            # print('** jury contention')
            return 0

    return float(fitness) / max_score
    # return fitness


def display(solution):
    print(solution)
    for team_planning in solution:
        line = ['..'] * 35
        for m, t in enumerate(team_planning[:3]):
            line[t] = "M%d" % (m + 1)
        t = team_planning[-1]
        line[t:t+2] = ['J-', '--', '--']
        print(' '.join(line))


def PlanningInitializator(genome, **args):
    genome.clearList()

    for i in xrange(genome.getHeight()):
        match_slots = random.sample(MATCH_SLOTS, MATCH_COUNT)
        for j, slot in enumerate(match_slots):
            genome.setItem(i, j, slot)
        jury_slots = set(JURY_SLOTS_SET)
        for slot in match_slots:
            jury_slots -= {slot, slot - 1, slot - 2}

        genome.setItem(i, JURY_POS, random.choice(list(jury_slots)))

    # print(genome.genomeList)


def noop(genome, **args):
    return 0


def main():
    genome = G2DList(7, 4)
    genome.setParams(rangemin=0, rangemax=MAX_SLOTS)

    genome.evaluator.set(eval_function)
    genome.crossover.set(Crossovers.G2DListCrossoverSingleHPoint)
    # genome.mutator.set(Mutators.G2DListMutatorSwap)
    genome.mutator.set(noop)
    genome.initializator.set(PlanningInitializator)

    ga = GSimpleGA(genome)
    ga.setGenerations(1000)
    ga.setPopulationSize(10000)
    ga.terminationCriteria.set(ConvergenceCriteria)

    ga.evolve(freq_stats=500)

    best = ga.bestIndividual()
    if best.fitness == 1.:
        print('!! SUCCESS !!')
    else:
        print("Sorry, no valid planning found :( Here is the best so far.")

    display(best.genomeList)
    print('fitness: %f' % best.fitness)

if __name__ == '__main__':
    main()