def get_nested(d, *keys):
    """
    Get a nested value from a dictionary by following a sequence of keys.

    Args:
        d (dict): The dictionary to search in.
        *keys: A sequence of keys to follow.

    Returns:
        The value at the nested key, or None if any key is not found.

    Example:
        >>> get_nested({"a": {"b": {"c": 1}}}, "a", "b", "c")
        1
        >>> get_nested({"a": {"b": {"c": 1}}}, "a", "b", "d")
        None
    """
    for key in keys:
        if isinstance(d, dict) and key in d:
            d = d[key]
        else:
            return None
    return d
