# import scispacy
# import spacy
# import en_core_sci_scibert
import re


# from spacy import displacy
# from scispacy.abbreviation import AbbreviationDetector
# from scispacy.umls_linking import UmlsEntityLinker

# nlp = spacy.load("en_core_sci_scibert")
#
# text = "XYREM (SOLUTION OXYBATE) ORAL SOLUTION, 500MG/ML"
#
# doc = nlp(text)
# print(list(doc.sents))
# print(doc.ents)


#  Hard cleaning rules:
#  \/([0-9]*)\/ --> Regex for removing stuff like DRUGNAME   /000123213/, occurs a lot!
#  long entries > 50 chars
#  too much data between parentheses
#  noisy punct
#  drug mentioned multiple times
#  generic non-descript names


def remove_stray_digits(string: str) -> str:
    return re.sub(pattern="\/([0-9]*)\/", repl="", string=string).strip()


def remove_long_entries(string: str) -> str:
    if len(string) >= 50:
        return "<LONGENT>"
    return string


def remove_data_between_parentheses(string: str) -> str:
    raise NotImplementedError


def remove_noisy_punct(string: str) -> str:
    """
    Removes non-essential punctuation from drug entries, e.g. "^VERAPAMIL^" receives a lower scoring due to the inclusion
    of the caret signs. Punctuation that conveys critical information however, should be left untouched such as hyphens
    that are included in drug names or "/" for units.
    """
    raise NotImplementedError


def remove_redundancy(string: str) -> str:
    words = string.split()
    return " ".join(sorted(set(words), key=words.index))


def remove_nondesc(string: str) -> str:
    nondesc_list = _load_dict_file("../data/nondesc_list.txt")
    if string in nondesc_list:
        return "<NONDESC>"
    return string


def _load_dict_file(path: str):
    with open(path, mode="r", encoding="utf-8") as f:
        lines = [line for line in f.readline()]
    return lines


a = remove_stray_digits("DRUGNAME   /000123213/")
b = remove_redundancy("DRUGNAME DRUGNAME 20 MG/KG")
print(a)
print(b)
