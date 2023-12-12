from z3 import *


def to_z3array(values, name, val_sort, idx_sort=IntSort()):
    """
    Create a Z3 array symbol storing the values in the given array

    :param list values: array of raw values to be stored
    :param str name: name of the Array symbol to be created
    :param Sort val_sort: sort of each value in the array
    :param Sort idx_sort: sort to use for the array's indexes (defaults to Int)

    :return: Z3 Array
    """
    output = Array(name, idx_sort, val_sort)
    for idx, ls in enumerate(values):
        output = Store(output, idx, ls)

    return output


def min_z3(values):
    """
    Create a Z3 expression return equating to the minimum of the given symbols

    Arguments:
        values: list, list of Z3 symbols/variables to find the min of

    Returns:
        a formula equating to the min value
    """
    m = values[0]
    for val in values[1:]:
        m = If(val < m, val, m)
    return m


def max_z3(values):
    """
    Create a Z3 expression return equating to the maximum of the given symbols

    Arguments:
        values: list, list of Z3 symbols/variables to find the max of

    Returns:
        a formula equating to the max value
    """
    m = values[0]
    for val in values[1:]:
        m = If(val > m, val, m)
    return m