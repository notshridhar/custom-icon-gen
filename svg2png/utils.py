# Utils Module
# ----------------
# contains some helper functions commonly used


def find_dict_keys(dictionary: dict, func):
    """ Get keys that satisfy function """
    return [key for key in dictionary.keys() if func(key)]
