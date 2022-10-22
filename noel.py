#!/bin/python3

from random import *
from schema import Schema, SchemaError
import time
import yaml


class ChristmasException(Exception):
    pass


class BadRandomSolutionException(Exception):
    pass


def uses_forbidden_group(solution, groups):
    for transaction in solution.items():
        for group in groups:
            if transaction[0] in group and transaction[1] in group:
                return True
    return False


def is_forbidden_transaction(solution, forbidden_transactions):
    for transaction in solution.items():
        for forbidden_t in forbidden_transactions:
            if transaction[0] == forbidden_t['giver'] and transaction[1] == forbidden_t['receiver']:
                return True
    return False


def try_generate_random_solution(participants):
    givers = set(participants)
    receivers = set(participants)
    solution = {}
    for giver in givers:
        potential_receivers = set(receivers)
        if giver in potential_receivers:
            potential_receivers.remove(giver)
        if not potential_receivers:
            raise BadRandomSolutionException
        index = randrange(0, len(potential_receivers))
        receiver = list(potential_receivers)[index]
        solution[giver] = receiver
        receivers.remove(receiver)
    return solution


def load_configuration():
    # Load configuration
    config = yaml.safe_load(open('config.yml'))

    # Check that the format of the configuration is correct
    config_schema = Schema({
        'participants': [str],
        'forbidden_groups': [[str]],
        'forbidden_transactions': [{'giver': str, 'receiver': str}]
    })
    try:
        config_schema.validate(config)
    except SchemaError as se:
        raise ChristmasException(f'Bad configuration : {se}')

    # Check that the names in forbidden groups and transactions are correct (to avoid spelling mistakes...)
    participants = config['participants']
    forbidden_groups = config['forbidden_groups']
    forbidden_transactions = config['forbidden_transactions']
    for group in forbidden_groups:
        for name in group:
            if name not in participants:
                raise ChristmasException(f'Bad configuration : {name} is mentioned in the forbidden groups, '
                                         f'but this person is not one of the participants')
    for transaction in forbidden_transactions:
        if transaction['giver'] not in participants or transaction['receiver'] not in participants:
            raise ChristmasException(f'Bad configuration : {name} is mentioned in the forbidden transactions, '
                                     f'but this person is not one of the participants')

    # If we reach this point, the configuration is valid
    return participants, forbidden_groups, forbidden_transactions


def main():
    (participants, forbidden_groups, forbidden_transactions) = load_configuration()
    seed(time.time())
    valid_solution_found = False
    while not valid_solution_found:
        try:
            solution = try_generate_random_solution(participants)
            if not uses_forbidden_group(solution, forbidden_groups) \
                    and not is_forbidden_transaction(solution, forbidden_transactions):
                valid_solution_found = True
        except BadRandomSolutionException:
            # random generation failed, we have to try again, nothing to do here
            pass

    for transaction in solution.items():
        giver = transaction[0].ljust(10, ' ')
        receiver = transaction[1]
        print(f'{giver} --> {receiver}')


if __name__ == '__main__':
    try:
        main()
    except ChristmasException as ce:
        print(f'ERROR : {ce}')
