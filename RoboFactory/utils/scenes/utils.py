def merge_dicts(base, custom):
    """Recursively merge dictionaries, with custom dict taking precedence."""
    for key, value in custom.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            merge_dicts(base[key], value)
        else:
            if value is None and key in base:
                del(base[key])
            elif value is not None:
                base[key] = value
    return base