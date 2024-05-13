import os

import locale

from backend.python.genetic_algorithm import GeneticAlgorithm


def main():
    locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')

    current_path = os.path.dirname(os.path.abspath(__file__))
    parent_path = os.path.abspath(os.path.join(current_path, os.pardir))

    file_input = f'{parent_path}/../data/data.xlsx'
    max_investment_period = 45
    max_budget = 150000
    file_output = f'{parent_path}/../output'

    ga = GeneticAlgorithm(f'{parent_path}/config.json')

    ga.precalculate(file_input, max_investment_period)

    ga.run(max_budget)

    ga.save_solution(file_output)


if __name__ == '__main__':
    main()
