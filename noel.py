#!/bin/python3
import argparse
import itertools
import logging
import sys
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
                raise ChristmasException(f'Bad configuration : {name} is mentioned in the forbidden groups, '
                                         f'but {name} is not a participant')
    for transaction in forbidden_transactions:
        if transaction.giver not in participants or transaction.receiver not in participants:
            raise ChristmasException(f'Bad configuration : {name} is mentioned in the forbidden transactions, '
                                     f'but {name} is not a participant')

    # If we reach this point, the configuration is valid
    return participants, forbidden_groups, forbidden_transactions


def computes_solution(rand_seed, config):
    """ Computes and return a valid solution, if it finds one """
    (participants, forbidden_groups, forbidden_transactions) = config
    seed(rand_seed)
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


def main():
    """
        Assign to each participant another participant to whom he must give a gift,
        taking into account some constraints given by the configuration
    """
    try:
        logging.basicConfig(format='%(levelname)s - %(message)s', stream=sys.stdout, level=logging.INFO)
        (rand_seed, config_file_path) = get_arguments()
        config = load_configuration(config_file_path)
        solution = computes_solution(rand_seed, config)
        for transaction in solution:
            logging.info(f'{transaction.giver.ljust(10, " ")} --> {transaction.receiver}')

    except ChristmasException as ce:
        logging.error(ce)


if __name__ == '__main__':
    main()
