# coding: utf-8
from __future__ import division  # non-trunc division by default

import decimal
import itertools
import operator
import re

FUNCTION_FOR_OPERATOR = {'/': operator.div, '*': operator.mul,
                         "-": operator.sub, "+": operator.add,
                         "**": operator.pow}
OPERATOR_FOR_FUNC_NAME = {'div': '/', "mul": "*", "pow": "**", "sub": "-", "add": "+"}
OPERATOR_FOR_FUNCTION = {v: k for k, v in FUNCTION_FOR_OPERATOR.items()}


def dround(decimal_number, decimal_places):
    # print "drounding", decimal_number, "to", decimal_places
    return decimal_number.quantize(decimal.Decimal(10) ** -decimal_places)


def sdround(decimal_number, decimal_places):
    string = str(dround(decimal_number, decimal_places))
    idx = string.index(".")
    return string[:idx + decimal_places + 1]


def parse_and_normalize(data):
    data = data.splitlines()
    pat = "(\d*[A-Za-z\-]+)([\d\.]*)g"
    grav = [re.match(pat, k.strip()).groups() for k in data]

    # data is a string, and in terms of g so multiply by 9.81
    # also we convert to Decimal (default 28 place precision) for increased precision
    g = decimal.Decimal(9.81)
    return [(k[0], decimal.Decimal(k[1]) * g) for k in grav]


def filter_1_to_10(data):
    return [x for x in data if 1 <= x[2] <= 10]


def operator_permutations(gravities, accuracy=3, operators=['/', '*']):
    all_pairs = list(itertools.permutations(gravities, 2))
    results = []

    def test_pair(operation, val1, val2):
        result = operation(val1, val2)
        if not 0 <= result <= 15:
            # too big or small to be interesting
            return
        dist_to_int = abs(result - dround(result, 0))
        threshold = (decimal.Decimal(10) ** -(accuracy + 1)) * 5
        if dist_to_int <= threshold:
            results.append((pair, operation.__name__, result, dist_to_int))

    for pair in all_pairs:
        for op in operators:
            test_pair(FUNCTION_FOR_OPERATOR[op], pair[0][1], pair[1][1])

    results = filter_1_to_10(results)

    # sort in place by 'distance from nearest integer'
    results.sort(key=operator.itemgetter(3))

    return results


def print_results(results):
    def pretty_print(x):
        _get_name = lambda x: x[0]
        _get_gravity = lambda x: x[1]

        planets = x[0]
        planet_a = planets[0]
        planet_b = planets[1]
        operation = OPERATOR_FOR_FUNC_NAME[x[1]]
        operation_result = x[2]
        operation_result_almost_rounded = sdround(operation_result, decimal_places_of_accuracy + 1)
        operation_result_rounded = sdround(operation_result, decimal_places_of_accuracy)
        distance_from_integer = "%.1e" % float(x[3])  # scientific notation
        print _get_name(planet_a), operation, _get_name(planet_b), \
            '=', \
            _get_gravity(planet_a), operation, _get_gravity(planet_b), \
            '=', operation_result_almost_rounded, "(rounded", operation_result_rounded, ") delta:",\
            distance_from_integer

    for x in results:
        pretty_print(x)


def div2(a, b):
    return a / b


if __name__ == "__main__":
    # from wikipedia: https://en.wikipedia.org/wiki/Surface_gravity
    data = """Sun28.02g
    Mercury0.38g
    Venus0.904g
    Earth1.00g
    Moon0.1654g
    Mars0.376g
    Phobos0.0005814g
    Deimos0.000306g
    Ceres0.0275g
    Jupiter2.53g
    Io0.183g
    Europa0.134g
    Ganymede0.15g
    Callisto0.126g
    Saturn1.07g
    Titan0.14g
    Enceladus0.0113g
    Uranus0.89g
    Neptune1.14g
    Triton0.0797g
    Pluto0.067g
    Eris0.0677g
    67P-CG0.000017g"""

    grav_ms = parse_and_normalize(data)

    decimal_places_of_accuracy = 1

    interesting_combinations = operator_permutations(grav_ms,
                                                     accuracy=decimal_places_of_accuracy,
                                                     operators=["+", "-", "/", "*", "**"])

    print_results(reversed(interesting_combinations))
    print "=============="
    print "nearest to integer printed last, with accuracy %ddp" % decimal_places_of_accuracy
    print "total results:", len(interesting_combinations)
