"""Contains string utility functions."""


def is_any_empty(*args):
    """Return true if any field is empty."""
    return any(arg.strip() == "" for arg in args)
