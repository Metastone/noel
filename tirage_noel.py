#!/bin/python3

from random import *
import time

def check(attributions, interdictions):
    for attribution in attributions.items():
        for interdiction in interdictions:
            if attribution[0] in interdiction and attribution[1] in interdiction:
                return False
    return True


def main():
    interdictions = [
            ['Isabelle', 'Hugo', 'Nicolas', 'Lucie'],
            ['Christian', 'Marie'],
            ['Jean', 'Claude'],
    ]
    seed(time.time())
    ok = False
    names = {'Isabelle', 'Hugo', 'Nicolas', 'Lucie', 'Julien', 'Claude', 'Jean', 'Marie', 'Christian'}
    while not ok:
        gifters = set(names)
        receivers = set(names)
        attributions = {}
        fail = False
        for gifter in gifters:
            potential_receivers = set(receivers)
            if gifter in potential_receivers:
                potential_receivers.remove(gifter)
            if not potential_receivers:
                fail = True
                break
            index = randrange(0, len(potential_receivers))
            receiver = list(potential_receivers)[index]
            attributions[gifter] = receiver
            receivers.remove(receiver)
        
        if fail:
            ok = False
        else:
            ok = check(attributions, interdictions)

    for attribution in attributions.items():
        gifter = attribution[0].ljust(10, ' ')
        receiver = attribution[1]
        print(f'{gifter} Donne à {receiver}')


if __name__ == "__main__":
    main()

