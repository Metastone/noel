#!/bin/python3
import argparse
import itertools
from random import *
from schema import Schema, SchemaError
from dataclasses import dataclass
import time
import yaml


class ChristmasException(Exception):
    pass


class BadRandomSolutionException(Exception):
    pass


@dataclass
class Transaction:
    """ Represent a association between a gift giver and a gift receiver """
    giver: str
    receiver: str


def no_forbidden_group(solution, groups):
    """ Return true if the solution is compliant with the 'forbidden groups' constraint """
    for (transaction, group) in itertools.product(solution, groups):
        if transaction.giver in group and transaction.receiver in group:
            return False
    return True


def no_forbidden_transaction(solution, forbidden_transactions):
    """ Return true if the solution is compliant with the 'forbidden transaction' constraint """
    for (t, f_t) in itertools.product(solution, forbidden_transactions):
        if t.giver == f_t.giver and t.receiver == f_t.receiver:
            return False
    return True


def try_generate_random_solution(participants):
    """
    Try to generate a random solution (list of Transaction(giver, receiver)), using a very basic algorithm.
    It fails by raising an exception if at the end, the last giver can only give a gift to himself
    """
    givers = list(participants)
    receivers = list(participants)
    solution = []
    for giver in givers:
        potential_receivers = list(receivers)
        if giver in potential_receivers:
            potential_receivers.remove(giver)
        if not potential_receivers:
            raise BadRandomSolutionException
        index = randrange(0, len(potential_receivers))
        receiver = potential_receivers[index]
        solution += [Transaction(giver, receiver)]
        receivers.remove(receiver)
    return solution


def load_configuration():
    """ Load the configuration from a YAML configuration file and return it """

    # Load YAML configuration file
    config = yaml.safe_load(open('config.yml'))

    # Check that the format of the loaded configuration is correct
    config_schema = Schema({
        'participants': [str],
        'forbidden_groups': [[str]],
        'forbidden_transactions': [{'giver': str, 'receiver': str}]
    })
    try:
        config_schema.validate(config)
    except SchemaError as se:
        raise ChristmasException(f'Bad configuration : {se}')

    # Reformat the configuration
    participants = config['participants']
    forbidden_groups = config['forbidden_groups']
    forbidden_transactions = [Transaction(t['giver'], t['receiver']) for t in config['forbidden_transactions']]

    # Check that the names in forbidden groups and forbidden transactions are correct (to avoid spelling mistakes...)
    for group in forbidden_groups:
        for name in group:
            if name not in participants:
                raise ChristmasException(f'Bad configuration : {name} is mentioned in the forbidden groups, '
                                         f'but this person is not one of the participants')
    for transaction in forbidden_transactions:
        if transaction.giver not in participants or transaction.receiver not in participants:
            raise ChristmasException(f'Bad configuration : {name} is mentioned in the forbidden transactions, '
                                     f'but this person is not one of the participants')

    # If we reach this point, the configuration is valid
    return participants, forbidden_groups, forbidden_transactions


def computes_solution(seed_for_rand):
    """ Computes and return a valid solution, if it finds one """
    (participants, forbidden_groups, forbidden_transactions) = load_configuration()
    seed(seed_for_rand)
    valid_solution_found = False
    while not valid_solution_found:
        try:
            solution = try_generate_random_solution(participants)
            if no_forbidden_group(solution, forbidden_groups) \
                    and no_forbidden_transaction(solution, forbidden_transactions):
                valid_solution_found = True
        except BadRandomSolutionException:
            # random generation failed, we have to try again, nothing to do here
            pass
    return solution


def get_arguments():
    """ Parses arguments from command line """
    parser = argparse.ArgumentParser(description='Organize a gift exchange')
    parser.add_argument('--seed', type=int, help='Seed to use for random operations (integer).'
                                                 ' If not present, the current time is used.')
    args = parser.parse_args()
    return args.seed if args.seed else time.time()


def main():
    """
        Assign to each participant another participant to whom he must give a gift,
        taking into account some constraints given by the configuration
    """
    try:
        seed_for_rand = get_arguments()
        solution = computes_solution(seed_for_rand)
        for transaction in solution:
            print(f'{transaction.giver.ljust(10, " ")} --> {transaction.receiver}')

    except ChristmasException as ce:
        print(f'ERROR : {ce}')


if __name__ == '__main__':
    main()
