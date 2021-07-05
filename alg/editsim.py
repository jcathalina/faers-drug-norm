import Levenshtein


def editsim(a: str, b: str, ignore_order=False) -> int:
    """
    returns a score from 0 - 100 indicating the similarity score based on the edit distance between two strings.
    NOTE: if clause at the beginning is specific for this notebook's experiments.
    """
    try:
        if a == "" or b == "<NA>":
            return 0

        longer, shorter = a, b
        if len(a) < len(b):
            longer, shorter = b, a

        lonlen = len(longer)

        if ignore_order:
            longer = " ".join(sorted(longer.split(" ")))
            shorter = " ".join(sorted(shorter.split(" ")))

        return int(((lonlen - Levenshtein.distance(longer, shorter)) / lonlen) * 100)
    except TypeError:
        return 0
