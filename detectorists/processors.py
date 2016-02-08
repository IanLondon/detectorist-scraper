import logging

def to_int(s, fallback=0):
    """Try to cast an int to a string. If you can't, return the fallback value"""
    try:
        result = int(s)
    except ValueError:
        logging.warning("Couldn't cast %s to int" % s)
        result = fallback

    return result
