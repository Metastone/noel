#!/bin/python3

from random import *
import time


class SolutionException(Exception):
    pass


def usesForbiddenGroup(solution, groups):
    for transaction in solution.items():
        for group in groups:
            if transaction[0] in group and transaction[1] in group:
                return True
    return False


def tryGenerateRandomSolution():
    gifters = set(names)
    receivers = set(names)
    solution = {}
    fail = False
    for gifter in gifters:
        potential_receivers = set(receivers)
        if gifter in potential_receivers:
            potential_receivers.remove(gifter)
        if not potential_receivers:
            raise SolutionException
        index = randrange(0, len(potential_receivers))
        receiver = list(potential_receivers)[index]
        solution[gifter] = receiver
        receivers.remove(receiver)
    return solution


groups = [
        ['Isabelle', 'Hugo', 'Nicolas', 'Lucie'],
        ['Christian', 'Marie'],
        ['Jean', 'Claude'],
] 
names = {'Isabelle', 'Hugo', 'Nicolas', 'Lucie', 'Julien', 'Claude', 'Jean', 'Marie', 'Christian'}


def main():
    seed(time.time())
    while True:
        try:
            solution = tryGenerateRandomSolution()
            if not usesForbiddenGroup(solution, groups):
                break
        except SolutionException:
            pass

    for transaction in solution.items():
        gifter = transaction[0].ljust(10, ' ')
        receiver = transaction[1]
        print(f'{gifter} offre à {receiver}')


if __name__ == "__main__":
    main()

