#!/bin/python3
import argparse
import itertools
import logging
import math
import random
import sys
from random import seed

from tqdm import tqdm
from schema import Schema, SchemaError
from dataclasses import dataclass
import time
import yaml


def get_arguments():
    """ Get the program arguments from command line """
    parser = argparse.ArgumentParser(description='Organize a gift exchange')
    parser.add_argument('--seed', type=int, help='Seed to use for random operations (integer).'
                                                 ' If not present, the current time is used.')
    args = parser.parse_args()

    # Getting seed to use for random generation
    if args.seed:
        logging.info(f'Using the used-defined seed for random operations : {args.seed}')
        rand_seed = args.seed
    else:
        rand_seed = time.time()
        logging.info(f'Using the current time ({rand_seed}) as a seed for random operations')

    # Getting configuration file path
    config_file_path = 'config.yml'
    logging.info(f'Using the configuration file {config_file_path}')

    return rand_seed, config_file_path


def spelling_error(name, forbidden_kind):
    """ Helper method used in configuration consistency checking """
    return ChristmasException(f'Bad configuration : {name} is mentioned in the forbidden {forbidden_kind}, '
                              f'but {name} is not a participant')


def load_configuration(config_file_path):
    """ Load the configuration from a YAML configuration file and return it """

    # Load YAML configuration file
    config = yaml.safe_load(open(config_file_path))

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
                raise spelling_error(name, 'groups')
    for transaction in forbidden_transactions:
        if transaction.giver not in participants:
            raise spelling_error(transaction.giver, 'transactions')
        if transaction.receiver not in participants:
            raise spelling_error(transaction.receiver, 'transactions')

    # If we reach this point, the configuration is valid
    return participants, forbidden_groups, forbidden_transactions


class ChristmasException(Exception):
    pass


class NoMorePotentialSolutionException(Exception):
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


def give_to_himself(solution):
    """ Return true if a participant gives a gift to himself """
    for transaction in solution:
        if transaction.giver == transaction.receiver:
            return True
    return False


def find_solution(it, config, progress_bar):
    """
        Look of a solution compliant with the given constraints, by iterating over all potential solutions.
        Return the solution if found, or throw an exception if all potential solutions have been exhausted.
    """
    (participants, forbidden_groups, forbidden_transactions) = config
    while True:
        try:
            progress_bar.update(1)
            receivers = next(it)
            solution = [Transaction(participants[i], receivers[i]) for i in range(len(participants))]
            if not give_to_himself(solution) and no_forbidden_group(solution, forbidden_groups)\
                    and no_forbidden_transaction(solution, forbidden_transactions):
                return solution
        except StopIteration:
            raise NoMorePotentialSolutionException


def get_solutions(config):
    participants = config[0]
    progress_bar = tqdm(total=math.factorial(len(participants)), leave=False)
    solutions = []
    it = itertools.permutations(participants)
    nb_solutions = 0
    while True:
        try:
            solutions += [find_solution(it, config, progress_bar)]
            nb_solutions += 1
        except NoMorePotentialSolutionException:
            break
    progress_bar.close()
    logging.info(f'{nb_solutions} solutions found')
    return solutions


def main():
    try:
        logging.basicConfig(format='%(levelname)s - %(message)s', stream=sys.stdout, level=logging.INFO)
        (rand_seed, config_file_path) = get_arguments()
        config = load_configuration(config_file_path)

        logging.info('Compute all solutions and choose one randomly...')
        seed(rand_seed)
        solutions = get_solutions(config)
        if len(solutions) == 0:
            raise ChristmasException('No solutions found')
        solution = random.choice(solutions)

        # Print solution
        logging.info('********** SOLUTION **********')
        for transaction in solution:
            logging.info(f'{transaction.giver.ljust(10, " ")} --> {transaction.receiver}')

    except ChristmasException as ce:
        logging.error(ce)


if __name__ == '__main__':
    main()
