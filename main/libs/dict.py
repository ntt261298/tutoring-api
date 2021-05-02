from copy import deepcopy


def merge_dict_recursively(a, b):
    """recursively merges dict's. not just simple a['key'] = b['key'], if
    both a and b have a key who's value is a dict then merge_dict_recursively
    is called on both values and the result stored in the returned
    dictionary."""
    if not isinstance(b, dict):
        return b
    result = deepcopy(a)
    for k, v in b.items():
        if k in result and isinstance(result[k], dict):
            result[k] = merge_dict_recursively(result[k], v)
        else:
            result[k] = deepcopy(v)
    return result


def merge_dicts(*dicts):
    """
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    https://stackoverflow.com/questions/38987/how-to-merge-two-dictionaries-in-a-single-expression
    """
    result = {}
    for dictionary in dicts:
        result = merge_dict_recursively(result, dictionary)
    return result


def get_dict_by_key_val(dictionaries: list, key, value) -> dict:
    """
    Loops through a list of dictionaries, returns the first one that has specified key & value
    :param dictionaries: a list of dictionaries
    example: [
        {
            "id": 123
        },
        {
            "id": 345
        }
    ]
    :param key: desired key
    :param value: desired value
    :return: the first dictionary which has specified key & value
    example: {
        "id": 123
    }
    """
    if not dictionaries:
        return {}
    for dictionary in dictionaries:
        if not isinstance(dictionary, dict):
            continue
        if dictionary.get(key) == value:
            return dictionary
    return {}
