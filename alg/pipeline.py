import spacy
import json

from spacy.language import Language, Doc
from spacy.matcher import PhraseMatcher
from typing import *


@spacy.registry.misc("abbreviations.dict.rxnorm")
def create_rxnorm_abbreviations_dict() -> Dict[str, str]:
    with open(file="../data/dictionaries/abbreviations.json", mode="r", encoding="utf-8") as f:
        abbreviations: Dict[str, str] = json.load(f)
    return abbreviations


@Language.factory("abbreviations", default_config={"abbreviations": {"@misc": "abbreviations.dict.rxnorm"},
                                                   "case_sensitive": False})
def create_abbreviation_component(nlp: Language, name: str, abbreviations: Dict[str, str], case_sensitive: bool):
    return AbbreviationComponent(nlp=nlp, abbreviations=abbreviations, case_sensitive=case_sensitive)


class AbbreviationComponent:
    def __init__(self, nlp: Language, abbreviations: Dict[str, str], case_sensitive: bool):
        matcher_attr = "TEXT" if case_sensitive else "LOWER"
        self.matcher = PhraseMatcher(nlp.vocab, attr=matcher_attr)
        self.matcher.add("ABBREVIATIONS", [nlp.make_doc(abb) for abb in abbreviations])
        self.abbreviations = abbreviations
        self.case_sensitive = case_sensitive

        if not Doc.has_extension("abbreviations"):
            Doc.set_extension("abbreviations", default=[])

    def __call__(self, doc: Doc) -> Doc:

        for _, start, end in self.matcher(doc):
            span = doc[start:end]
            abbreviation = self.abbreviations.get(span.text if self.case_sensitive else span.text.lower())
            doc._.abbreviations.append((span, abbreviation))

        return doc


# spacy.prefer_gpu()
# # nlp = spacy.load("en_core_web_sm")
# nlp = spacy.blank("en")
# nlp.add_pipe("abbreviations", config={"case_sensitive": False})
#
# # doc = nlp("acet 200 mg tablet")
# # print(doc._.abbreviations)
#
# import pandas as pd
#
# # a = pd.read_csv("../data/processed/drug_table_clean.csv", usecols=["drugname", "prod_ai"], nrows=10000, dtype="object")
# # a = a["drugname"].to_list()
# a = ["INJ MG HCL something tablet"]
#
# for x in a:
#     doc = nlp(x)
#     # print(f"Doc: {doc}, Abbr: {doc._.abbreviations}")
#     print(doc)

from spacy.lang.en import English


class AbbreviationHandler:
    def __init__(self, abbrev_dict):
        self.abbrev_dict = abbrev_dict

    def __call__(self, doc):
        for token in doc:
            token.norm_ = self.abbrev_dict.get(token.text.lower(), token.norm_)
        return doc


@Language.factory("abbreviation_handler")
def create_abbreviation_handler(nlp: Language, name: str):
    with open(file="../data/dictionaries/abbreviations.json", mode="r", encoding="utf-8") as f:
        abbreviations: Dict[str, str] = json.load(f)
    return AbbreviationHandler(abbreviations)


def expand_abbreviations(list_to_expand: List[str]):
    nlp = English()
    nlp.add_pipe("abbreviation_handler")

    for item in list_to_expand:
        if not isinstance(item, str):
            item = "nan"
        p_item = " ".join([token.norm_ for token in nlp(item)])
        yield p_item


# a = [token.norm_ for token in nlp("INJ mg hcl something tablet")]
# print(" ".join(a))
import pandas as pd

# test = pd.read_csv("../data/processed/drug_table_clean.csv", usecols=["drugname", "prod_ai"], chunksize=250, nrows=1000)
# with open("abbrev_test.csv", mode="a", encoding="utf-8") as f:
#     for chunk in test:
#         test_list = chunk["drugname"].to_list()
#         p_test_list = expand_abbreviations(test_list)
#         for item in p_test_list:
#             f.write(f"{item}\n")


nlp = spacy.load("en_core_web_sm")
doc = nlp("Paracetamol accuprinil 500 mg tablet")

for token in doc.ents:
    print(token.text, token.label_)

#
# x = expand_abbreviations(test_list)
# y = list(x)
# print(y)
