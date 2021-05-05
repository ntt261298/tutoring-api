def equal(x, y):
    """Check if float x and float y are approximately equal"""

    return abs(x - y) <= 1e-9


def greater_than_or_equal(x, y):
    return (x > y) or equal(x, y)


def less_than_or_equal(x, y):
    return (x < y) or equal(x, y)


def in_range(number, low, high):
    return greater_than_or_equal(number, low) and less_than_or_equal(number, high)
