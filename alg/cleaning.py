from typing import List

import scispacy
import spacy
# import en_core_sci_scibert
import en_ner_bc5cdr_md
import re
import pandas as pd


# from scispacy.umls_linking import UmlsEntityLinker

# nlp = spacy.load("en_core_sci_scibert")
#
# text = "XYREM (SOLUTION OXYBATE) ORAL SOLUTION, 500MG/ML"
#
# doc = nlp(text)
# print(list(doc.sents))
# print(doc.ents)


"""
Hard cleaning rules:
\/([0-9]*)\/ --> Regex for removing stuff like DRUGNAME   /000123213/, occurs a lot!
long entries > 50 chars
too much data between parentheses
noisy punct
drug mentioned multiple times
generic non-descript names
"""


def remove_stray_digits(string: str) -> str:
    return re.sub(pattern="\/([0-9]*)\/", repl="", string=string).strip()


def remove_data_between_parentheses(string: str) -> str:
    no_paren = re.sub(pattern=r"\([^()]*\)", repl="", string=string).strip()
    if len(no_paren) == 0:
        return string
    return no_paren


def remove_noisy_punct(string: str, _nlp: spacy.Language) -> str:
    """
    Removes non-essential punctuation from drug entries, e.g. "^VERAPAMIL^" receives a lower scoring due to the inclusion
    of the caret signs. Punctuation that conveys critical information however, should be left untouched such as hyphens
    that are included in drug names or "/" for units.
    """
    doc = _nlp(string)
    return " ".join(token.lemma_ for token in doc if not token.is_punct)


def remove_redundancy(string: str) -> str:
    words = string.split()
    return " ".join(sorted(set(words), key=words.index))


def remove_nondesc(string: str, nondesc_list: List[str]) -> str:
    if string in nondesc_list:
        return ""
    return string


def _load_dict_file(path: str):
    with open(path, mode="r", encoding="utf-8") as f:
        lines = [line for line in f.readline()]
    return lines


def _load_entries(path: str):
    df = pd.read_csv(path, usecols=["query"])
    return df["query"].fillna("NA").to_list()


def clean(_entries, _nlp, _nondesc_list):
    """
    - all stand-alone "unknown" were replaced by "na" using the regex "^\bunknown+\b$" manually.
    - all remaining ^ signs were removed manually
    - all inline "unknown"s were removed manually
    - all "unnamed" were removed manually
    :param _entries:
    :param _nlp:
    :param _nondesc_list:
    :return:
    """
    for entry in _entries:
        s = entry.lower()
        s = remove_data_between_parentheses(s)
        s = remove_noisy_punct(s, _nlp)
        s = remove_redundancy(s)
        s = remove_stray_digits(s)
        s = remove_nondesc(s, _nondesc_list)
        yield s


if __name__ == "__main__":
    import csv

    nlp = spacy.load("en_ner_bc5cdr_md")
    nondesc_list = _load_dict_file("../data/nondesc_list.txt")
    entries = _load_entries("../results/exp_3_no_clean_no_int_fulldev.csv")

    cleaned_entries = list(clean(entries, nlp, nondesc_list))

    with open("../results/cleaned_queries.csv", mode="w", encoding="utf-8") as f:
        for entry in cleaned_entries:
            f.write(entry + "\n")

    print("DONE!")
